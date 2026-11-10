"""ConfidenceFilter - decides which predictions are trustworthy enough."""

from __future__ import annotations

from collections.abc import Iterable, Iterator

from .detection_models import Detection
from .exceptions import InvalidConfidenceError

#: Range offered by the threshold slider in the web UI (10 % .. 95 %).
MIN_THRESHOLD = 0.10
MAX_THRESHOLD = 0.95


class ConfidenceFilter:
    """Keeps only detections whose confidence reaches ``threshold``.

    OOP ideas: encapsulation (validated ``threshold`` property) and a
    GENERATOR in ``filter`` (results are produced one at a time, lazily).
    """

    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold

    @property
    def threshold(self) -> float:
        return self._threshold

    @threshold.setter
    def threshold(self, value: float) -> None:
        if not 0 < float(value) <= 1:
            raise InvalidConfidenceError(f"threshold {value!r} is outside (0, 1]")
        self._threshold = float(value)

    @classmethod
    def from_percent(cls, percent: float) -> "ConfidenceFilter":
        """Build a filter from the slider value (e.g. ``60`` -> 0.60).

        The value is clamped to 10..95 % exactly like the original application.
        """
        return cls(max(MIN_THRESHOLD, min(MAX_THRESHOLD, float(percent) / 100)))

    def is_reliable(self, detection: Detection | None) -> bool:
        """True if ``detection`` exists and reaches the threshold."""
        return detection is not None and detection.confidence >= self._threshold

    def filter(self, detections: Iterable[Detection]) -> Iterator[Detection]:
        """Yield only the reliable detections (generator)."""
        return (d for d in detections if self.is_reliable(d))
