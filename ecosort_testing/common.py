"""Shared error response model."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ErrorResult:
    subsystem: str
    code: str
    message: str
    http_status: int
    recoverable: bool

    def as_dict(self) -> dict:
        return {
            "subsystem": self.subsystem,
            "code": self.code,
            "error": self.message,
            "recoverable": self.recoverable,
        }
