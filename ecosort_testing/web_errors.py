"""Vijay Kathiresan: Web App and Dashboard error boundary."""
from .common import ErrorResult


class WebDashboardError(Exception):
    """Base exception for HTTP requests and integration failures."""


class MissingUploadError(WebDashboardError): pass
class InvalidRequestError(WebDashboardError): pass
class DatabaseOperationError(WebDashboardError): pass
class ServiceUnavailableError(WebDashboardError): pass


class WebDashboardErrorHandler:
    subsystem = "Web App, Dashboard and Integration"
    _mapping = {
        MissingUploadError: ("UPLOAD_REQUIRED", "Choose an image first.", 400, True),
        InvalidRequestError: ("INVALID_REQUEST", "The request is invalid.", 400, True),
        DatabaseOperationError: ("DATABASE_ERROR", "The record could not be saved.", 503, True),
        ServiceUnavailableError: ("SERVICE_UNAVAILABLE", "The prediction service is unavailable.", 503, True),
    }

    def handle(self, error: Exception) -> ErrorResult:
        code, message, status, recoverable = self._mapping.get(type(error), ("WEB_UNKNOWN", "An unexpected application error occurred.", 500, False))
        return ErrorResult(self.subsystem, code, message, status, recoverable)
