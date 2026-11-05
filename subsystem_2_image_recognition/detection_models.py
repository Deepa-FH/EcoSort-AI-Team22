from dataclasses import dataclass

@dataclass
class BoundingBox:
    """Encapsulates detected object coordinates; owned by Prasad Hule."""
    x: float = 0; y: float = 0; width: float = 0; height: float = 0
    def initialize(self) -> None:
        if self.width < 0 or self.height < 0: raise ValueError("Dimensions cannot be negative.")
    def get_area(self) -> float: return self.width * self.height
    def set_size(self, width: float, height: float) -> None:
        if width < 0 or height < 0: raise ValueError("Dimensions cannot be negative.")
        self.width, self.height = width, height

class DetectionResult:
    """Stores one model prediction; owned by Prasad Hule."""
    def __init__(self, label: str, confidence: float, model_version: str, box: BoundingBox | None = None) -> None:
        self._label, self._model_version, self._box = label, model_version, box
        self._confidence = 0.0; self.set_confidence(confidence)
    def initialize(self) -> None:
        if not self._label: raise ValueError("Prediction label is required.")
    def get_label(self) -> str: return self._label
    def set_label(self, value: str) -> None:
        if not value.strip(): raise ValueError("Label cannot be empty.")
        self._label = value
    def get_confidence(self) -> float: return self._confidence
    def set_confidence(self, value: float) -> None:
        if not 0 <= value <= 1: raise ValueError("Confidence must be between 0 and 1.")
        self._confidence = float(value)
    def get_model_version(self) -> str: return self._model_version
