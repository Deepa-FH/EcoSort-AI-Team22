from dataclasses import dataclass


@dataclass(frozen=True)
class BoundingBox:
    x1: float
    y1: float
    x2: float
    y2: float

    def as_list(self) -> list[float]:
        return [round(value, 1) for value in (self.x1, self.y1, self.x2, self.y2)]


@dataclass(frozen=True)
class Detection:
    label: str
    confidence: float
    box: BoundingBox

    @property
    def confidence_percent(self) -> float:
        return round(self.confidence * 100, 1)
