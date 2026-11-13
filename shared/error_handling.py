"""Shared error-handling building blocks used by all four subsystems.

OOP idea shown here: INHERITANCE.
    * ``EcoSortError`` is the root of every exception in the project.
    * Each subsystem defines its own base exception that inherits from it
      (``PreprocessingError``, ``RecognitionError`` ...).
    * Each subsystem also defines an error-handler class that inherits from
      ``BaseErrorHandler`` and turns *any* exception into a safe ``ErrorResponse``.

Why: the web layer must never show a stack trace, file path or API detail to
the user (see the PPT non-functional requirement "Avoid exposing stack traces").
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass

logger = logging.getLogger("ecosort")


@dataclass(frozen=True)
class ErrorResponse:
    """A safe, user-facing description of an error (what the web layer returns).

    Attributes:
        subsystem:   which subsystem produced the error (for debugging).
        code:        short machine-readable code, e.g. ``MODEL_NOT_FOUND``.
        message:     friendly text that is safe to show to the user.
        http_status: HTTP status the web layer should answer with.
        recoverable: True if the user can simply try again.
    """

    subsystem: str
    code: str
    message: str
    http_status: int
    recoverable: bool

    def to_dict(self) -> dict:
        """Return the response as a plain dict (ready for ``jsonify``)."""
        return asdict(self)


class EcoSortError(Exception):
    """Root exception of the whole project.

    Subclasses only override the four class attributes below; they do not need
    their own ``__init__``. ``detail`` holds technical info for the server log
    and is NEVER sent to the user.
    """

    code = "ECOSORT_ERROR"
    safe_message = "Something went wrong. Please try again."
    http_status = 500
    recoverable = False

    def __init__(self, detail: str | None = None):
        super().__init__(detail or self.safe_message)
        self.detail = detail or self.safe_message


class BaseErrorHandler:
    """Turns exceptions into ``ErrorResponse`` objects.

    Subclasses only set ``subsystem``; the logic is shared (code re-use through
    inheritance).
    """

    subsystem = "shared"

    def handle(self, error: BaseException) -> ErrorResponse:
        """Convert ``error`` into a safe response and log the technical detail.

        DEBUG: the full technical message is printed on the server console
        through the ``ecosort`` logger; look there when a user reports an error.
        """
        if isinstance(error, EcoSortError):
            logger.warning("[%s] %s: %s", self.subsystem, error.code, error.detail)
            return ErrorResponse(self.subsystem, error.code, error.safe_message,
                                 error.http_status, error.recoverable)
        # Unknown exception: log everything, tell the user nothing technical.
        logger.exception("[%s] unexpected error", self.subsystem, exc_info=error)
        return ErrorResponse(self.subsystem, "UNEXPECTED_ERROR",
                             "Something went wrong. Please try again.", 500, False)
