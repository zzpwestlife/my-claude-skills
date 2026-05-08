from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Mapping, TypeVar

ENV_USERNAME = "GEEKTIME_USERNAME"
ENV_PASSWORD = "GEEKTIME_PASSWORD"


class AuthError(ValueError):
    """Raised when credentials are missing or invalid."""


class SessionInvalidError(RuntimeError):
    """Raised when a server rejects a session token."""


@dataclass(frozen=True)
class Credentials:
    username: str
    password: str


@dataclass(frozen=True)
class Session:
    token: str
    expires_at: datetime


def load_credentials(
    config: Mapping[str, object] | None,
    environ: Mapping[str, str] | None = None,
) -> Credentials:
    env = environ or os.environ
    env_username = env.get(ENV_USERNAME, "").strip()
    env_password = env.get(ENV_PASSWORD, "").strip()
    if env_username and env_password:
        return Credentials(username=env_username, password=env_password)

    source = config or {}
    nested = source.get("credentials")
    if isinstance(nested, Mapping):
        cfg_username = str(nested.get("username", "")).strip()
        cfg_password = str(nested.get("password", "")).strip()
    else:
        cfg_username = str(source.get("username", "")).strip()
        cfg_password = str(source.get("password", "")).strip()

    if cfg_username and cfg_password:
        return Credentials(username=cfg_username, password=cfg_password)

    raise AuthError(
        "Missing credentials. Set GEEKTIME_USERNAME/GEEKTIME_PASSWORD "
        "or provide username/password in config."
    )


T = TypeVar("T")


class AuthService:
    def __init__(
        self,
        *,
        session_file: Path | str,
        login: Callable[[Credentials], Session],
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self._session_file = Path(session_file)
        self._login = login
        self._now = now or (lambda: datetime.now(timezone.utc))

    def get_session(self, credentials: Credentials) -> Session:
        cached = self._load_session()
        if cached and self._is_valid(cached):
            return cached

        return self._login_and_persist(credentials)

    def execute_with_auto_recover(
        self,
        credentials: Credentials,
        operation: Callable[[str], T],
    ) -> T:
        session = self.get_session(credentials)
        try:
            return operation(session.token)
        except SessionInvalidError:
            self.invalidate_session()
            refreshed = self._login_and_persist(credentials)
            return operation(refreshed.token)

    def invalidate_session(self) -> None:
        if self._session_file.exists():
            self._session_file.unlink()

    def _login_and_persist(self, credentials: Credentials) -> Session:
        session = self._login(credentials)
        self._save_session(session)
        return session

    def _is_valid(self, session: Session) -> bool:
        return session.expires_at > self._now()

    def _save_session(self, session: Session) -> None:
        payload = {"token": session.token, "expires_at": session.expires_at.isoformat()}
        self._session_file.parent.mkdir(parents=True, exist_ok=True)
        self._session_file.write_text(json.dumps(payload), encoding="utf-8")

    def _load_session(self) -> Session | None:
        if not self._session_file.exists():
            return None

        try:
            payload = json.loads(self._session_file.read_text(encoding="utf-8"))
            token = str(payload["token"]).strip()
            expires_at = datetime.fromisoformat(str(payload["expires_at"]))
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
            return None

        if not token:
            return None

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        return Session(token=token, expires_at=expires_at)
