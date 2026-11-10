"""DashboardService - numbers and exports for the Dashboard page."""

from __future__ import annotations

import csv
import io

from .waste_repository import WasteRepository

#: ILLUSTRATIVE sample data for the municipality view (not real measurements).
#: The dashboard labels it "sample". Replace with real figures if they exist.
MUNICIPALITY_SAMPLE = {
    "areas": [
        {"name": "Dortmund-Mitte", "street": "Kampstraße", "recycling_rate": 68, "monthly_tons": 124},
        {"name": "Hörde", "street": "Hörder Bahnhofstraße", "recycling_rate": 74, "monthly_tons": 91},
        {"name": "Hombruch", "street": "Harkortstraße", "recycling_rate": 71, "monthly_tons": 83},
        {"name": "Aplerbeck", "street": "Köln-Berliner-Straße", "recycling_rate": 77, "monthly_tons": 76},
        {"name": "Bochum", "street": "Kortumstraße", "recycling_rate": 64, "monthly_tons": 118},
        {"name": "Lünen", "street": "Lange Straße", "recycling_rate": 61, "monthly_tons": 69},
    ],
    "monthly": [62, 64, 66, 65, 69, 72, 70, 74, 76, 75, 78, 80],
}


class DashboardService:
    """Builds the JSON for the charts and the CSV export."""

    def __init__(self, repository: WasteRepository, waste_labels_provider):
        """``waste_labels_provider`` is a function returning the current rule labels
        (so the filter list always matches the admin-edited rules)."""
        self._repository = repository
        self._waste_labels = waste_labels_provider

    def get_statistics(self, filters: dict[str, list[str]] | None = None) -> dict:
        """Real scan statistics + the clearly-labelled municipality sample."""
        stats = self._repository.stats(filters)
        stats["filters"]["waste"] = sorted(self._waste_labels())
        stats["municipality"] = MUNICIPALITY_SAMPLE
        return stats

    def export_history_csv(self, limit: int = 1000) -> str:
        """All recent scans as CSV text (PPT: "Export summary to CSV")."""
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["id", "created_at", "user", "model_label", "confidence", "bin_label",
                         "source", "llm_tokens", "city", "image"])
        for scan in self._repository.history(limit):
            writer.writerow([scan["id"], scan["created_at"], scan.get("username") or "",
                             scan["model_label"] or "", scan["model_confidence"] or "",
                             scan["predicted_bin"] or "", scan["prediction_source"],
                             scan["llm_tokens"], scan["city"], scan["image_path"]])
        return buffer.getvalue()
