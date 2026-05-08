from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from geektime_exporter.auth import (
    AuthError,
    AuthService,
    Credentials,
    Session,
    SessionInvalidError,
    load_credentials,
)


def test_load_credentials_env_overrides_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEEKTIME_USERNAME", "env-user")
    monkeypatch.setenv("GEEKTIME_PASSWORD", "env-pass")

    creds = load_credentials({"username": "config-user", "password": "config-pass"})

    assert creds == Credentials(username="env-user", password="env-pass")


def test_load_credentials_fallback_to_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GEEKTIME_USERNAME", raising=False)
    monkeypatch.delenv("GEEKTIME_PASSWORD", raising=False)

    creds = load_credentials({"username": "config-user", "password": "config-pass"})

    assert creds == Credentials(username="config-user", password="config-pass")


def test_load_credentials_missing_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GEEKTIME_USERNAME", raising=False)
    monkeypatch.delenv("GEEKTIME_PASSWORD", raising=False)

    with pytest.raises(AuthError):
        load_credentials({})


def test_login_persists_and_reuses_session(tmp_path: Path) -> None:
    calls = {"count": 0}
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)

    def login(_: Credentials) -> Session:
        calls["count"] += 1
        return Session(token=f"token-{calls['count']}", expires_at=now + timedelta(hours=1))

    service = AuthService(session_file=tmp_path / "session.json", login=login, now=lambda: now)
    creds = Credentials(username="u", password="p")

    first = service.get_session(creds)
    second = service.get_session(creds)

    assert first.token == "token-1"
    assert second.token == "token-1"
    assert calls["count"] == 1
    assert (tmp_path / "session.json").exists()


def test_expired_session_triggers_relogin(tmp_path: Path) -> None:
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    session_file = tmp_path / "session.json"
    session_file.write_text(
        json.dumps(
            {
                "token": "old-token",
                "expires_at": (now - timedelta(seconds=1)).isoformat(),
            }
        ),
        encoding="utf-8",
    )

    calls = {"count": 0}

    def login(_: Credentials) -> Session:
        calls["count"] += 1
        return Session(token="new-token", expires_at=now + timedelta(hours=1))

    service = AuthService(session_file=session_file, login=login, now=lambda: now)
    result = service.get_session(Credentials(username="u", password="p"))

    assert result.token == "new-token"
    assert calls["count"] == 1


def test_invalid_session_auto_recovers(tmp_path: Path) -> None:
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    session_file = tmp_path / "session.json"
    session_file.write_text(
        json.dumps(
            {
                "token": "cached-token",
                "expires_at": (now + timedelta(hours=1)).isoformat(),
            }
        ),
        encoding="utf-8",
    )

    login_calls = {"count": 0}
    operation_tokens: list[str] = []

    def login(_: Credentials) -> Session:
        login_calls["count"] += 1
        return Session(token="fresh-token", expires_at=now + timedelta(hours=1))

    def operation(token: str) -> str:
        operation_tokens.append(token)
        if token == "cached-token":
            raise SessionInvalidError("session invalid")
        return "ok"

    service = AuthService(session_file=session_file, login=login, now=lambda: now)
    result = service.execute_with_auto_recover(
        Credentials(username="u", password="p"),
        operation,
    )

    assert result == "ok"
    assert login_calls["count"] == 1
    assert operation_tokens == ["cached-token", "fresh-token"]
