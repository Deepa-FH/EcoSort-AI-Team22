"""Exception handling and testable boundaries for EcoSort AI."""
from .common import ErrorResult
from .dataset_errors import DatasetErrorHandler
from .recognition_errors import RecognitionErrorHandler
from .recycling_ai_errors import RecyclingAIErrorHandler
from .web_errors import WebDashboardErrorHandler

__all__ = ["ErrorResult", "DatasetErrorHandler", "RecognitionErrorHandler", "RecyclingAIErrorHandler", "WebDashboardErrorHandler"]
