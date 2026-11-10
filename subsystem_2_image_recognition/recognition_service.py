"""ImageRecognitionService - the single entry point of Subsystem 2."""

from __future__ import annotations

from PIL import Image

from .confidence_filter import MAX_THRESHOLD, MIN_THRESHOLD, ConfidenceFilter
from .detection_models import PredictionResult
from .detector import WasteDetector


class ImageRecognitionService:
    """Combines the detector and the confidence filter into one call.

    Other subsystems (Subsystem 4) only know this class, not YOLO. That is
    ABSTRACTION: the model could be replaced without touching the web app
    (PPT requirement "Allow future model replacement").
    """

    def __init__(self, detector: WasteDetector, default_threshold: float = 0.5):
        self._detector = detector
        self._default_threshold = float(default_threshold)

    @property
    def detector(self) -> WasteDetector:
        return self._detector

    @property
    def default_threshold(self) -> float:
        return self._default_threshold

    @default_threshold.setter
    def default_threshold(self, value: float) -> None:
        # The filter validates the range for us.
        self._default_threshold = ConfidenceFilter(value).threshold

    def start(self) -> None:
        """Load the model immediately (called once when the app starts)."""
        self._detector.load()

    def recognize(self, image: Image.Image, threshold_percent: float | None = None) -> PredictionResult:
        """Analyse ``image`` and return a ``PredictionResult``.

        Args:
            image: RGB image from Subsystem 1.
            threshold_percent: the user's slider value (10..95). ``None`` uses
                the default.
        """
        if threshold_percent is None:
            conf_filter = ConfidenceFilter(max(MIN_THRESHOLD, min(MAX_THRESHOLD, self._default_threshold)))
        else:
            conf_filter = ConfidenceFilter.from_percent(threshold_percent)
        detections = self._detector.predict(image)
        return PredictionResult(
            detections=tuple(detections),
            threshold=conf_filter.threshold,
            image_size=image.size,
            model_version=self._detector.model_version,
        )
