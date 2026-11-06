"""Subsystem 4: Vijay Kathiresan — Web App, Dashboard and Integration."""
from .waste_sorting_web_app import WasteSortingWebApp
from .integration_controller import IntegrationController
from .dashboard_service import DashboardService
from .waste_repository import WasteRepository
__all__ = ["WasteSortingWebApp", "IntegrationController", "DashboardService", "WasteRepository"]
