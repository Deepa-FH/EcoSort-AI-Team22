"""Data classes of Subsystem 2: BoundingBox, Detection and PredictionResult.

OOP idea: these are small immutable VALUE OBJECTS (``frozen=True``): once
created they cannot be modified, which prevents accidental changes while the
object travels between subsystems.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class BoundingBox:
    """Rectangle around a detected object, in pixels (top-left, bottom-right)."""

    x1: float
    y1: float
    x2: float
    y2: float

    def as_list(self) -> list[float]:
        """Coordinates rounded to 1 decimal - the format the web UI receives."""
        return [round(value, 1) for value in (self.x1, self.y1, self.x2, self.y2)]

    @property
    def area(self) -> float:
        """Box area in square pixels."""
        return max(0.0, self.x2 - self.x1) * max(0.0, self.y2 - self.y1)


@dataclass(frozen=True)
class Detection:
    """One object found by the model: label + confidence + box."""

    label: str
    confidence: float          # 0.0 .. 1.0
    box: BoundingBox

    @property
    def confidence_percent(self) -> float:
        """Confidence as percent, e.g. 0.753 -> 75.3."""
        return round(self.confidence * 100, 1)

    def to_dict(self) -> dict:
        """JSON-friendly form used by ``/api/analyze``."""
        return {"label": self.label, "confidence": round(self.confidence, 4),
                "box": self.box.as_list()}


@dataclass(frozen=True)
class PredictionResult:
    """Everything the rest of the system needs to know about one image.

    ``needs_review`` is True when the best detection is below the user's
    threshold (or nothing was found) - then Subsystem 3 asks the LLM.
    """

    detections: tuple[Detection, ...] = field(default_factory=tuple)
    threshold: float = 0.5
    image_size: tuple[int, int] = (0, 0)   # (width, height)
    model_version: str = "unknown"

    @property
    def top(self) -> Detection | None:
        """The most confident detection, or ``None`` if nothing was found."""
        return self.detections[0] if self.detections else None

    @property
    def needs_review(self) -> bool:
        top = self.top
        return top is None or top.confidence < self.threshold

    def to_dict(self) -> dict:
        """Dict merged into the JSON answer of ``/api/analyze``."""
        return {
            "detections": [d.to_dict() for d in self.detections],
            "top": self.top.to_dict() if self.top else None,
            "needs_review": self.needs_review,
            "threshold": round(self.threshold, 2),
            "image_size": list(self.image_size),
            "model_version": self.model_version,
        }
