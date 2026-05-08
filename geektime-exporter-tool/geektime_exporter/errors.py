from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ExporterError(Exception):
    code: str
    message: str
    context: dict[str, object] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


class AuthFailureError(ExporterError):
    def __init__(self, message: str, context: dict[str, object] | None = None) -> None:
        super().__init__("AUTH_FAILURE", message, context or {})


class NetworkError(ExporterError):
    def __init__(self, message: str, context: dict[str, object] | None = None) -> None:
        super().__init__("NETWORK_ERROR", message, context or {})


class ParseError(ExporterError):
    def __init__(self, message: str, context: dict[str, object] | None = None) -> None:
        super().__init__("PARSE_ERROR", message, context or {})


class RetryExhaustedError(ExporterError):
    def __init__(self, message: str, context: dict[str, object] | None = None) -> None:
        super().__init__("RETRY_EXHAUSTED", message, context or {})
