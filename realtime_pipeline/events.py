"""Domain events passed through the real-time processing pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class BoundingBox:
    x1: int
    y1: int
    x2: int
    y2: int

    @property
    def width(self) -> int:
        return max(0, self.x2 - self.x1)

    @property
    def height(self) -> int:
        return max(0, self.y2 - self.y1)

    @property
    def area(self) -> int:
        return self.width * self.height

    @property
    def aspect_ratio(self) -> float:
        return self.height / max(1, self.width)


@dataclass
class RecognitionEvent:
    """One on-the-fly optical-sorter event."""
    frame_number: int
    timestamp_seconds: float
    frame: Any
    model_label: str = "Unknown"
    confidence: float = 0.0
    bounding_box: BoundingBox | None = None
    visual_tags: set[str] = field(default_factory=set)
    material_category: str = "Unclassified"
    routing_code: str = "ROUTE_REVIEW_99"
    accepted: bool = True
    status_message: str = "Pending processing"

    def clone(self, **changes: Any) -> "RecognitionEvent":
        values = self.__dict__.copy()
        values.update(changes)
        values["visual_tags"] = set(values["visual_tags"])
        return RecognitionEvent(**values)
