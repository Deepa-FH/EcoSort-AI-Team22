from collections.abc import Callable
from .confidence_filter import ConfidenceFilter
from .detection_models import DetectionResult

class WasteDetector:
    """Provides the prediction interface; owned by Prasad Hule."""
    def __init__(self, model_name: str, confidence_filter: ConfidenceFilter) -> None:
        self._model_name, self._confidence_filter, self._predictor = model_name, confidence_filter, None
    def initialize(self, predictor: Callable[[dict], list[DetectionResult]]) -> None: self._predictor = predictor
    def get_model_name(self) -> str: return self._model_name
    def set_model_name(self, value: str) -> None:
        if not value.strip(): raise ValueError("Model name cannot be empty.")
        self._model_name = value
    def get_confidence_filter(self) -> ConfidenceFilter: return self._confidence_filter
    def set_confidence_filter(self, value: ConfidenceFilter) -> None: self._confidence_filter = value
    def predict(self, image: dict) -> DetectionResult:
        if self._predictor is None: raise RuntimeError("Detector is not initialized.")
        accepted = [x for x in self._predictor(image) if self._confidence_filter.accept(x)]
        if not accepted: raise ValueError("No prediction passed the confidence threshold.")
        return max(accepted, key=lambda x: x.get_confidence())
