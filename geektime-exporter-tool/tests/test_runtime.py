from __future__ import annotations

import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from geektime_exporter.auth import Credentials, Session
from geektime_exporter.errors import AuthFailureError, NetworkError, RetryExhaustedError
from geektime_exporter.runtime import (
    RuntimeOptions,
    _build_browser_login,
    _build_hybrid_fetcher,
    _looks_like_spa_shell,
    classify_exception,
    run_export,
)


def test_classify_exception_for_network_error() -> None:
    err = classify_exception(urllib.error.URLError("down"))
    assert isinstance(err, NetworkError)
    assert err.code == "NETWORK_ERROR"


def test_run_export_retries_and_logs(tmp_path: Path) -> None:
    calls = {"count": 0}

    def flaky_fetcher(url: str, headers: dict[str, str]) -> str:
        calls["count"] += 1
        if calls["count"] < 3:
            raise urllib.error.URLError("temporary")
        return """
        <article>
          <h1>重试成功</h1>
          <p>正文</p>
          <img src="https://img.example.com/a.png" />
        </article>
        """

    def login_func(credentials: Credentials) -> Session:
        return Session(
            token=f"token-{credentials.username}",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )

    options = RuntimeOptions(
        article="https://time.geekbang.org/column/article/100",
        batch=None,
        output=str(tmp_path / "out"),
        images_dir=str(tmp_path / "out" / "assets"),
        naming="slug",
        retries=3,
    )
    config = {
        "username": "u",
        "password": "p",
        "log_file": str(tmp_path / "out" / "run.log"),
    }
    exit_code = run_export(
        options,
        config,
        login_func=login_func,
        fetcher=flaky_fetcher,
        downloader=lambda _url: b"img",
        sleep_fn=lambda _s: None,
    )

    assert exit_code == 0
    assert calls["count"] == 3
    files = list((tmp_path / "out").glob("*.md"))
    assert len(files) == 1
    assert "重试成功" in files[0].read_text(encoding="utf-8")
    log_text = (tmp_path / "out" / "run.log").read_text(encoding="utf-8")
    assert "retry attempt=1/3" in log_text


def test_run_export_fails_after_retries(tmp_path: Path) -> None:
    def always_fail(_url: str, _headers: dict[str, str]) -> str:
        raise urllib.error.URLError("offline")

    def login_func(_credentials: Credentials) -> Session:
        return Session(
            token="token",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )

    options = RuntimeOptions(
        article="https://time.geekbang.org/column/article/100",
        batch=None,
        output=str(tmp_path / "out"),
        images_dir=str(tmp_path / "out" / "assets"),
        naming="slug",
        retries=2,
    )
    config = {"username": "u", "password": "p"}

    with pytest.raises(RetryExhaustedError):
        run_export(
            options,
            config,
            login_func=login_func,
            fetcher=always_fail,
            sleep_fn=lambda _s: None,
        )


def test_run_export_browser_mode_works_without_username_password(tmp_path: Path) -> None:
    def fetcher(_url: str, _headers: dict[str, str]) -> str:
        return """
        <article>
          <h1>浏览器登录导出</h1>
          <p>正文</p>
        </article>
        """

    def browser_login(_credentials: Credentials) -> Session:
        return Session(
            token="cookie:session_id=abc; uid=1",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )

    options = RuntimeOptions(
        article="https://time.geekbang.org/column/article/200",
        batch=None,
        output=str(tmp_path / "out"),
        images_dir=str(tmp_path / "out" / "assets"),
        naming="slug",
        retries=1,
    )
    config = {
        "auth_mode": "browser",
        "browser_login_url": "https://time.geekbang.org/",
        "log_file": str(tmp_path / "out" / "run.log"),
    }
    exit_code = run_export(
        options,
        config,
        login_func=browser_login,
        fetcher=fetcher,
        downloader=lambda _url: b"img",
        sleep_fn=lambda _s: None,
    )

    assert exit_code == 0
    files = list((tmp_path / "out").glob("*.md"))
    assert len(files) == 1


def test_run_export_relogin_when_session_invalid(tmp_path: Path) -> None:
    seen_tokens: list[str] = []
    login_calls = {"count": 0}

    def login_func(_credentials: Credentials) -> Session:
        login_calls["count"] += 1
        token = "old-token" if login_calls["count"] == 1 else "new-token"
        return Session(
            token=token,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )

    def fetcher(_url: str, headers: dict[str, str]) -> str:
        token = headers.get("Authorization", "").replace("Bearer ", "")
        seen_tokens.append(token)
        if token == "old-token":
            from geektime_exporter.auth import SessionInvalidError

            raise SessionInvalidError("expired")
        return """
        <article>
          <h1>自动重登成功</h1>
          <p>正文</p>
        </article>
        """

    options = RuntimeOptions(
        article="https://time.geekbang.org/column/article/201",
        batch=None,
        output=str(tmp_path / "out"),
        images_dir=str(tmp_path / "out" / "assets"),
        naming="slug",
        retries=1,
    )
    config = {"username": "u", "password": "p"}

    exit_code = run_export(
        options,
        config,
        login_func=login_func,
        fetcher=fetcher,
        sleep_fn=lambda _s: None,
    )

    assert exit_code == 0
    assert seen_tokens[:2] == ["old-token", "new-token"]
    assert login_calls["count"] == 2


def test_build_browser_login_prefers_cdp(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def fake_cdp(**kwargs):  # type: ignore[no-untyped-def]
        calls.append("cdp")
        return type(
            "Result",
            (),
            {
                "cookie_header": "sid=abc",
                "expires_at": datetime.now(timezone.utc) + timedelta(hours=1),
            },
        )()

    def fake_fallback(**kwargs):  # type: ignore[no-untyped-def]
        calls.append("fallback")
        raise AssertionError("fallback should not be used")

    import geektime_exporter.runtime as runtime

    monkeypatch.setattr(runtime, "login_with_cdp_session", fake_cdp)
    monkeypatch.setattr(runtime, "login_with_browser_session", fake_fallback)
    login = _build_browser_login({"browser_cdp_url": "http://127.0.0.1:9222"})
    session = login(Credentials(username="browser", password="browser"))

    assert calls == ["cdp"]
    assert session.token.startswith("cookie:")


def test_build_browser_login_cdp_unavailable_strict_fail(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_cdp(**kwargs):  # type: ignore[no-untyped-def]
        raise AuthFailureError("cdp unavailable")

    import geektime_exporter.runtime as runtime

    monkeypatch.setattr(runtime, "login_with_cdp_session", fake_cdp)
    login = _build_browser_login({"browser_cdp_required": True})

    with pytest.raises(AuthFailureError, match="cdp unavailable"):
        login(Credentials(username="browser", password="browser"))


def test_looks_like_spa_shell() -> None:
    assert _looks_like_spa_shell('<html><body><div id="app"></div><script src="/main.js"></script></body></html>')
    assert not _looks_like_spa_shell("<html><body><article><p>content</p></article></body></html>")


def test_hybrid_fetcher_switches_to_cdp_render(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def fake_http_fetch(url: str, headers: dict[str, str]) -> str:
        calls.append("http")
        return '<html><body><div id="app"></div><script src="/main.js"></script></body></html>'

    def fake_render(**kwargs):  # type: ignore[no-untyped-def]
        calls.append("cdp")
        return "<html><body><article><p>rendered</p></article></body></html>"

    import geektime_exporter.runtime as runtime
    import logging

    monkeypatch.setattr(runtime, "_http_fetch", fake_http_fetch)
    monkeypatch.setattr(runtime, "fetch_rendered_page_via_cdp", fake_render)
    fetcher = _build_hybrid_fetcher("http://127.0.0.1:9222", logging.getLogger("test"))
    html = fetcher("https://time.geekbang.org/column/article/1", {"Cookie": "a=b"})

    assert calls == ["http", "cdp"]
    assert "rendered" in html
