"""Subsystem 4 - Web App, Dashboard & Integration (owner: Vijay Kathiresan)."""
from .app_config import AppConfig
from .application_factory import create_application
from .dashboard_service import DashboardService
from .database import Database
from .exceptions import (AuthenticationError, JobNotFoundError, MissingUploadError, PermissionDeniedError,
                         StorageError, UserExistsError, ValidationFailedError, WebDashboardError,
                         WebDashboardErrorHandler)
from .integration_controller import IntegrationController
from .review_jobs import ReviewJobManager
from .scan_service import ScanOutcome, ScanService
from .tunnel_manager import TunnelManager
from .user_repository import AuthService, UserRepository
from .waste_repository import WasteRepository
from .waste_sorting_web_app import WasteSortingWebApp

__all__ = [
    "AppConfig", "create_application", "WasteSortingWebApp", "IntegrationController", "ScanService",
    "ScanOutcome", "ReviewJobManager", "DashboardService", "Database", "WasteRepository",
    "UserRepository", "AuthService", "TunnelManager", "WebDashboardError", "AuthenticationError",
    "PermissionDeniedError", "MissingUploadError", "ValidationFailedError", "UserExistsError",
    "JobNotFoundError", "StorageError", "WebDashboardErrorHandler",
]
