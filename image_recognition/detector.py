from __future__ import annotations

from threading import Lock
from pathlib import Path
from PIL import Image

from .confidence_filter import ConfidenceFilter
from .detection_models import BoundingBox, Detection
from .exceptions import InvalidConfidenceError
from .model_loader import ModelLoader


class DetectionStream:
    """Iterator over detections, used for stream-style processing demonstrations."""
    def __init__(self, detections: list[Detection]):
        self._detections = detections
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self) -> Detection:
        if self._index >= len(self._detections):
            raise StopIteration
        item = self._detections[self._index]
        self._index += 1
        return item


class WasteDetector:
    def __init__(self, model_path: Path, threshold: float = 0.25, loader: ModelLoader | None = None):
        if not 0 < threshold <= 1:
            raise InvalidConfidenceError("Confidence must be greater than 0 and at most 1.")
        self.model = (loader or ModelLoader()).load(model_path)
        self.threshold = threshold
        self.filter = ConfidenceFilter(threshold)
        self.lock = Lock()
        self.labels = list(self.model.names.values())

    def predict(self, image: Image.Image) -> dict:
        with self.lock:
            result = self.model.predict(image, device="cpu", conf=self.threshold, imgsz=640, verbose=False)[0]
            detections = []
            for box in result.boxes:
                detections.append(Detection(
                    label=result.names[int(box.cls.item())],
                    confidence=float(box.conf.item()),
                    box=BoundingBox(*[float(value) for value in box.xyxy[0].tolist()]),
                ))
            detections = sorted(self.filter.filter(detections), key=lambda item: item.confidence, reverse=True)
            annotated = result.plot()
        from PIL import Image as PILImage
        return {"detections": [
            {"label": d.label, "confidence": round(d.confidence, 6), "confidence_percent": d.confidence_percent, "box": d.box.as_list()}
            for d in detections
        ], "count": len(detections), "labels": self.labels, "annotated_array": annotated}
