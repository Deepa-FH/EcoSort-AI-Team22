from __future__ import annotations

from collections.abc import Iterable, Iterator
from .detection_models import Detection


class ConfidenceFilter:
    def __init__(self, threshold: float = 0.25):
        self.threshold = threshold

    def filter(self, detections: Iterable[Detection]) -> Iterator[Detection]:
        return (item for item in detections if item.confidence >= self.threshold)
