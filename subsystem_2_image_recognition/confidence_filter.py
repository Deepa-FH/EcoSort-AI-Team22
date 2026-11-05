from .detection_models import DetectionResult

class ConfidenceFilter:
    """Rejects weak predictions; owned by Prasad Hule."""
    def __init__(self, threshold: float = 0.50) -> None:
        self._threshold = 0.0; self.set_threshold(threshold)
    def initialize(self, threshold: float | None = None) -> None:
        if threshold is not None: self.set_threshold(threshold)
    def get_threshold(self) -> float: return self._threshold
    def set_threshold(self, value: float) -> None:
        if not 0 <= value <= 1: raise ValueError("Threshold must be between 0 and 1.")
        self._threshold = float(value)
    def accept(self, result: DetectionResult) -> bool: return result.get_confidence() >= self._threshold
