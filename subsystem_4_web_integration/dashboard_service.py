class DashboardService:
    """Maintains dashboard statistics; owned by Vijay Kathiresan."""
    def __init__(self) -> None: self._scan_count, self._category_counts = 0, {}
    def initialize(self) -> None: self._scan_count, self._category_counts = 0, {}
    def get_scan_count(self) -> int: return self._scan_count
    def set_scan_count(self, value: int) -> None:
        if value < 0: raise ValueError("Scan count cannot be negative.")
        self._scan_count = value
    def record_scan(self, category: str) -> None:
        self._scan_count += 1; self._category_counts[category] = self._category_counts.get(category, 0) + 1
    def summary(self) -> dict: return {"total_scans": self._scan_count, "categories": dict(self._category_counts)}
