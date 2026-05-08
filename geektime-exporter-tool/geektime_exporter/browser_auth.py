from __future__ import annotations

import json
import time
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from .errors import AuthFailureError


@dataclass(frozen=True)
class BrowserSessionResult:
    cookie_header: str
    expires_at: datetime


def _validate_cookie(cookie_header: str, verify_url: str) -> bool:
    request = urllib.request.Request(
        verify_url,
        headers={
            "User-Agent": "geektime-exporter/0.1",
            "Cookie": cookie_header,
        },
    )
    try:
        with urllib.request.urlopen(request) as response:  # noqa: S310
            if response.status != 200:
                return False
            body = response.read().decode("utf-8", errors="ignore")
            return "error" not in body.lower()
    except Exception:  # noqa: BLE001
        return False


def login_with_browser_session(
    *,
    login_url: str,
    verify_url: str,
    timeout_seconds: int = 300,
    poll_interval_seconds: float = 1.5,
    browser_channel: str | None = None,
) -> BrowserSessionResult:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover
        raise AuthFailureError(
            "Browser auth requires playwright. Run: python3 -m pip install playwright"
        ) from exc

    with sync_playwright() as playwright:
        launch_kwargs: dict[str, object] = {"headless": False}
        if browser_channel:
            launch_kwargs["channel"] = browser_channel
        browser = playwright.chromium.launch(**launch_kwargs)
        context = browser.new_context()
        page = context.new_page()
        page.goto(login_url, wait_until="domcontentloaded")

        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            cookies = context.cookies("https://time.geekbang.org")
            if cookies:
                cookie_header = "; ".join(
                    f"{cookie['name']}={cookie['value']}" for cookie in cookies
                )
                if _validate_cookie(cookie_header, verify_url):
                    browser.close()
                    return BrowserSessionResult(
                        cookie_header=cookie_header,
                        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
                    )
            page.wait_for_timeout(int(poll_interval_seconds * 1000))

        browser.close()
        raise AuthFailureError("Browser login timeout: no valid session cookie detected")


def login_with_cdp_session(
    *,
    cdp_url: str,
    login_url: str,
    verify_url: str,
    timeout_seconds: int = 120,
    poll_interval_seconds: float = 1.0,
) -> BrowserSessionResult:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover
        raise AuthFailureError(
            "CDP auth requires playwright. Run: python3 -m pip install playwright"
        ) from exc

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.connect_over_cdp(cdp_url)
            contexts = browser.contexts
            if not contexts:
                raise AuthFailureError("CDP connected but no browser context found")
            context = contexts[0]

            page = context.pages[0] if context.pages else context.new_page()
            try:
                page.goto(login_url, wait_until="domcontentloaded", timeout=15000)
            except Exception:  # noqa: BLE001
                # Keep trying with current context cookies even if navigation fails.
                pass

            deadline = time.time() + timeout_seconds
            while time.time() < deadline:
                cookies = context.cookies("https://time.geekbang.org")
                if cookies:
                    cookie_header = "; ".join(
                        f"{cookie['name']}={cookie['value']}" for cookie in cookies
                    )
                    if _validate_cookie(cookie_header, verify_url):
                        browser.close()
                        return BrowserSessionResult(
                            cookie_header=cookie_header,
                            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
                        )
                page.wait_for_timeout(int(poll_interval_seconds * 1000))
            browser.close()
    except AuthFailureError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise AuthFailureError(
            f"Failed to connect CDP endpoint: {cdp_url}. "
            "Please start Chrome with remote debugging port first."
        ) from exc

    raise AuthFailureError("CDP connected but no valid logged-in session detected")


def fetch_rendered_page_via_cdp(
    *,
    cdp_url: str,
    page_url: str,
    timeout_ms: int = 15000,
) -> str:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover
        raise AuthFailureError(
            "CDP render requires playwright. Run: python3 -m pip install playwright"
        ) from exc

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.connect_over_cdp(cdp_url)
            contexts = browser.contexts
            if not contexts:
                raise AuthFailureError("CDP connected but no browser context found")
            context = contexts[0]
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(page_url, wait_until="domcontentloaded", timeout=timeout_ms)
            # Let SPA finish hydration if possible.
            try:
                page.wait_for_load_state("networkidle", timeout=timeout_ms)
            except Exception:  # noqa: BLE001
                pass
            html = page.content()
            browser.close()
            return html
    except AuthFailureError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise AuthFailureError(f"CDP render failed for {page_url}: {exc}") from exc


def session_to_payload(session: BrowserSessionResult) -> str:
    return json.dumps(
        {
            "token": f"cookie:{session.cookie_header}",
            "expires_at": session.expires_at.isoformat(),
        },
        ensure_ascii=True,
    )
