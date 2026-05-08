from __future__ import annotations

import json
import logging
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable

from .auth import (
    AuthError,
    AuthService,
    Credentials,
    Session,
    SessionInvalidError,
    load_credentials,
)
from .errors import AuthFailureError, ExporterError, NetworkError, ParseError, RetryExhaustedError
from .browser_auth import (
    fetch_rendered_page_via_cdp,
    login_with_browser_session,
    login_with_cdp_session,
)
from .markdown_export import export_batch_articles, export_single_article

LoginFunc = Callable[[Credentials], Session]


def _as_bool(value: object, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
    return bool(value)


@dataclass(frozen=True)
class RuntimeOptions:
    article: str | None
    batch: str | None
    output: str
    images_dir: str
    naming: str
    retries: int
    start_mode: str = "index"
    start_value: str | None = None


def create_logger(log_file: Path) -> logging.Logger:
    logger = logging.getLogger("geektime_exporter")
    if logger.handlers:
        return logger
    log_file.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(log_file, encoding="utf-8")
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
    handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger


def classify_exception(exc: Exception) -> ExporterError:
    if isinstance(exc, ExporterError):
        return exc
    if isinstance(exc, AuthError):
        return AuthFailureError(str(exc))
    if isinstance(exc, SessionInvalidError):
        return AuthFailureError("Session invalid", context={"reason": str(exc)})
    if isinstance(exc, urllib.error.URLError):
        return NetworkError(str(exc))
    if isinstance(exc, (ValueError, TypeError)):
        return ParseError(str(exc))
    return ExporterError("UNKNOWN_ERROR", str(exc))


def _build_http_login(config: dict[str, object]) -> LoginFunc:
    login_url = str(config.get("login_url", "")).strip()
    if not login_url:
        raise AuthFailureError("Missing login_url in config")

    def _login(credentials: Credentials) -> Session:
        payload = json.dumps(
            {"username": credentials.username, "password": credentials.password}
        ).encode("utf-8")
        request = urllib.request.Request(
            login_url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "geektime-exporter/0.1",
            },
            method="POST",
        )
        with urllib.request.urlopen(request) as response:  # noqa: S310
            body = json.loads(response.read().decode("utf-8"))
        token = str(body.get("token", "")).strip()
        ttl_seconds = int(body.get("expires_in", 3600))
        if not token:
            raise AuthFailureError("Login response missing token")
        return Session(
            token=token,
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=max(ttl_seconds, 60)),
        )

    return _login


def _build_browser_login(
    config: dict[str, object],
    *,
    browser_channel: str | None = None,
) -> LoginFunc:
    login_url = str(config.get("browser_login_url", "https://time.geekbang.org/")).strip()
    verify_url = str(
        config.get(
            "browser_verify_url",
            "https://time.geekbang.org/column/article/967091",
        )
    ).strip()
    timeout_seconds = int(config.get("browser_login_timeout_seconds", 300))
    cdp_url = str(config.get("browser_cdp_url", "http://127.0.0.1:9222")).strip()
    cdp_required = _as_bool(config.get("browser_cdp_required"), default=True)

    def _to_session(result) -> Session:  # type: ignore[no-untyped-def]
        return Session(token=f"cookie:{result.cookie_header}", expires_at=result.expires_at)

    def _login(_credentials: Credentials) -> Session:
        try:
            return _to_session(
                login_with_cdp_session(
                    cdp_url=cdp_url,
                    login_url=login_url,
                    verify_url=verify_url,
                    timeout_seconds=min(timeout_seconds, 120),
                )
            )
        except AuthFailureError as cdp_error:
            if cdp_required:
                raise AuthFailureError(
                    "CDP login required but unavailable. "
                    f"{cdp_error}. Start Chrome with: "
                    "open -na \"Google Chrome\" --args --remote-debugging-port=9222"
                ) from cdp_error

        session = login_with_browser_session(
            login_url=login_url,
            verify_url=verify_url,
            timeout_seconds=timeout_seconds,
            browser_channel=browser_channel,
        )
        return _to_session(session)

    return _login


def _retry(
    operation: Callable[[], object],
    *,
    retries: int,
    logger: logging.Logger,
    sleep_fn: Callable[[float], None],
) -> object:
    attempts = max(retries, 1)
    for index in range(1, attempts + 1):
        try:
            return operation()
        except Exception as raw_exc:  # noqa: BLE001
            err = classify_exception(raw_exc)
            logger.warning(
                "retry attempt=%s/%s code=%s message=%s",
                index,
                attempts,
                err.code,
                err.message,
            )
            if index >= attempts:
                raise RetryExhaustedError(
                    "Operation failed after retries",
                    context={"attempts": attempts, "error_code": err.code},
                ) from raw_exc
            sleep_fn(min(index * 0.5, 2.0))
    raise RetryExhaustedError("Operation failed unexpectedly")


def _http_fetch(url: str, headers: dict[str, str]) -> str:
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request) as response:  # noqa: S310
        return response.read().decode("utf-8", errors="ignore")


def _looks_like_spa_shell(html: str) -> bool:
    return '<div id="app"></div>' in html and "main.js" in html


def _build_hybrid_fetcher(cdp_url: str, logger: logging.Logger) -> Callable[[str, dict[str, str]], str]:
    def _fetch(url: str, headers: dict[str, str]) -> str:
        html = _http_fetch(url, headers)
        if _looks_like_spa_shell(html):
            logger.info("detected spa shell, switching to cdp render url=%s", url)
            return fetch_rendered_page_via_cdp(cdp_url=cdp_url, page_url=url)
        return html

    return _fetch


def run_export(
    options: RuntimeOptions,
    config: dict[str, object],
    *,
    login_func: LoginFunc | None = None,
    fetcher: Callable[[str, dict[str, str]], str] | None = None,
    downloader: Callable[[str], bytes] | None = None,
    environ: dict[str, str] | None = None,
    sleep_fn: Callable[[float], None] | None = None,
    browser_channel: str | None = None,
) -> int:
    output_dir = Path(options.output)
    images_dir = Path(options.images_dir)
    log_file = Path(str(config.get("log_file", output_dir / "export.log")))
    logger = create_logger(log_file)
    sleep = sleep_fn or time.sleep

    session_file = Path(str(config.get("session_file", output_dir / ".session.json")))
    auth_mode = str(config.get("auth_mode", "browser")).strip().lower()
    effective_browser_channel = browser_channel
    if effective_browser_channel is None:
        channel = str(config.get("browser_channel", "")).strip()
        effective_browser_channel = channel or None
    if auth_mode == "browser":
        credentials = Credentials(username="browser", password="browser")
        login = login_func or _build_browser_login(
            config,
            browser_channel=effective_browser_channel,
        )
        effective_fetcher = fetcher or _build_hybrid_fetcher(
            cdp_url=str(config.get("browser_cdp_url", "http://127.0.0.1:9222")).strip(),
            logger=logger,
        )
    else:
        credentials = load_credentials(config, environ=environ or os.environ)
        login = login_func or _build_http_login(config)
        effective_fetcher = fetcher
    auth = AuthService(session_file=session_file, login=login)

    def _export_with_token(token: str) -> object:
        if options.article:
            result = export_single_article(
                article_url=options.article,
                session_token=token,
                output_dir=output_dir,
                images_dir=images_dir,
                naming=options.naming,
                fetcher=effective_fetcher,
                downloader=downloader,
            )
            logger.info("exported article=%s file=%s", options.article, result.file_path)
            return [result]
        if not options.batch:
            raise ParseError("Either article or batch must be provided")
        results = export_batch_articles(
            column_url=options.batch,
            session_token=token,
            output_dir=output_dir,
            images_dir=images_dir,
            naming=options.naming,
            fetcher=effective_fetcher,
            downloader=downloader,
            start_index=int(options.start_value or "1")
            if options.start_mode == "index"
            else 1,
            start_article_id=options.start_value
            if options.start_mode == "article_id"
            else None,
        )
        logger.info("exported batch column=%s count=%s", options.batch, len(results))
        return results

    def _execute() -> object:
        return auth.execute_with_auto_recover(credentials, _export_with_token)

    try:
        _retry(_execute, retries=options.retries, logger=logger, sleep_fn=sleep)
    except Exception as exc:  # noqa: BLE001
        err = classify_exception(exc)
        logger.error("failed code=%s message=%s context=%s", err.code, err.message, err.context)
        raise
    return 0
