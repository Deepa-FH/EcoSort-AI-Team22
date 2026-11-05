class ApplicationCoordinator:
    """Connects web requests, business logic and dashboard; owned by Vijay Kathiresan."""
    def __init__(self, request_validator, controller, dashboard) -> None:
        self._request_validator, self._controller, self._dashboard = request_validator, controller, dashboard
    def initialize(self) -> None: self._request_validator.initialize(); self._controller.initialize()
    def get_dashboard(self): return self._dashboard
    def set_dashboard(self, value) -> None:
        if value is None: raise ValueError("Dashboard service is required.")
        self._dashboard = value
    def handle_demo_request(self, filename: str, content: bytes) -> dict:
        self._request_validator.validate(filename, content)
        response = self._controller.classify(filename, content)
        self._dashboard.record_scan(response["category"]); response["dashboard_scans"] = self._dashboard.get_scan_count()
        return response
