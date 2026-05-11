from __future__ import annotations

from geektime_exporter import browser_auth


class _DummyResponse:
    def __init__(self, *, status: int, body: str) -> None:
        self.status = status
        self._body = body

    def read(self) -> bytes:
        return self._body.encode("utf-8")

    def __enter__(self) -> "_DummyResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        return None


def test_validate_cookie_does_not_fail_on_generic_error_word(monkeypatch) -> None:
    def fake_urlopen(request):  # type: ignore[no-untyped-def]
        return _DummyResponse(
            status=200,
            body="<html><body><script>window.__error_monitor__=true;</script></body></html>",
        )

    monkeypatch.setattr(browser_auth.urllib.request, "urlopen", fake_urlopen)
    assert browser_auth._validate_cookie("sid=abc", "https://time.geekbang.org/") is True


def test_validate_cookie_fails_on_login_required_text(monkeypatch) -> None:
    def fake_urlopen(request):  # type: ignore[no-untyped-def]
        return _DummyResponse(status=200, body="<html><body>请先登录后查看</body></html>")

    monkeypatch.setattr(browser_auth.urllib.request, "urlopen", fake_urlopen)
    assert browser_auth._validate_cookie("sid=abc", "https://time.geekbang.org/") is False
