"""Subsystem 4 - exceptions and error handler (owner: Vijay Kathiresan).

    EcoSortError
      +-- WebDashboardError
            +-- AuthenticationError      (wrong username / password, session expired)
            +-- PermissionDeniedError    (admin-only page)
            +-- MissingUploadError       (no photo in the request)
            +-- ValidationFailedError    (bad form / JSON input; message is user-facing)
            +-- UserExistsError          (username already taken)
            +-- JobNotFoundError         (unknown review job)
            +-- StorageError             (photo/database could not be written)
"""

from shared.error_handling import BaseErrorHandler, EcoSortError


class WebDashboardError(EcoSortError):
    """Base class for web, session and storage problems."""

    code = "WEB_ERROR"
    safe_message = "The request could not be completed."
    http_status = 500


class AuthenticationError(WebDashboardError):
    code = "AUTH_REQUIRED"
    safe_message = "Authentication required. Please sign in again."
    http_status = 401
    recoverable = True


class PermissionDeniedError(WebDashboardError):
    code = "FORBIDDEN"
    safe_message = "You do not have permission to do that."
    http_status = 403


class MissingUploadError(WebDashboardError):
    code = "MISSING_UPLOAD"
    safe_message = "Please take or upload a photo first."
    http_status = 400
    recoverable = True


class ValidationFailedError(WebDashboardError):
    """Invalid user input. The message passed in IS shown to the user, so only
    pass friendly text here (never internal details)."""

    code = "VALIDATION_FAILED"
    http_status = 400
    recoverable = True

    def __init__(self, message: str):
        super().__init__(message)
        self.safe_message = message          # instance value overrides the class default


class UserExistsError(ValidationFailedError):
    code = "USER_EXISTS"

    def __init__(self):
        super().__init__("That username is already registered.")


class JobNotFoundError(WebDashboardError):
    code = "JOB_NOT_FOUND"
    safe_message = "Review not found."
    http_status = 404


class StorageError(WebDashboardError):
    code = "STORAGE_FAILED"
    safe_message = "The photo could not be saved."


class WebDashboardErrorHandler(BaseErrorHandler):
    """Error handler of Subsystem 4 (logic inherited from ``BaseErrorHandler``)."""

    subsystem = "web_dashboard"
