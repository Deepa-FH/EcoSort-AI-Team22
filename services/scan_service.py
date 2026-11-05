"""Business validation kept separate from Flask and SQL."""
from __future__ import annotations

from typing import Any


class ValidationError(ValueError):
    pass


class ScanService:
    REQUIRED = ("item_name", "material_category", "confidence", "disposal_bin", "city")

    def __init__(self, repository) -> None:
        self._repository = repository

    def normalize(self, payload: dict[str, Any]) -> dict[str, Any]:
        missing = [name for name in self.REQUIRED if payload.get(name) in (None, "")]
        if missing:
            raise ValidationError("Missing fields: " + ", ".join(missing))
        try:
            confidence = float(payload["confidence"])
        except (TypeError, ValueError) as exc:
            raise ValidationError("confidence must be a number") from exc
        if not 0 <= confidence <= 1:
            raise ValidationError("confidence must be between 0 and 1")
        return {
            "item_name": str(payload["item_name"]).strip(),
            "material_category": str(payload["material_category"]).strip(),
            "confidence": confidence,
            "disposal_bin": str(payload["disposal_bin"]).strip(),
            "city": str(payload["city"]).strip(),
            "notes": str(payload.get("notes", "")).strip(),
        }

    def list_scans(self): return self._repository.list_all()
    def get_scan(self, scan_id: int): return self._repository.get(scan_id)
    def create_scan(self, payload: dict[str, Any]): return self._repository.create(self.normalize(payload))
    def update_scan(self, scan_id: int, payload: dict[str, Any]): return self._repository.update(scan_id, self.normalize(payload))
    def delete_scan(self, scan_id: int): return self._repository.delete(scan_id)
    def statistics(self): return self._repository.statistics()
