"""WasteDetector (runs the model) and DetectionStream (an iterator)."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from threading import Lock

from PIL import Image

from .detection_models import BoundingBox, Detection
from .exceptions import InferenceError
from .model_loader import ModelLoader


def pick_device():
    """Return ``0`` (first GPU) if CUDA is available, otherwise ``"cpu"``.

    The Docker image is CPU-only, so there this always returns ``"cpu"``.
    """
    try:
        import torch
        return 0 if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"


class DetectionStream:
    """Iterator over a list of detections (shows the iterator protocol).

    ``for d in DetectionStream(items)`` works because the class defines
    ``__iter__`` and ``__next__``.
    """

    def __init__(self, detections: list[Detection]):
        self._detections = list(detections)
        self._index = 0

    def __iter__(self) -> "DetectionStream":
        return self

    def __next__(self) -> Detection:
        if self._index >= len(self._detections):
            raise StopIteration
        item = self._detections[self._index]
        self._index += 1
        return item


class WasteDetector:
    """Runs the YOLO model on one image and returns ``Detection`` objects.

    * The model is loaded lazily (on first use), through an injected ``ModelLoader``.
    * A ``Lock`` makes it thread-safe (Flask serves requests in several threads).
    """

    def __init__(self, model_path: Path | str, loader: ModelLoader | None = None,
                 min_confidence: float = 0.10, image_size: int = 640):
        self._model_path = Path(model_path)
        self._loader = loader or ModelLoader()
        self._min_confidence = float(min_confidence)   # model-level cut-off (not the user's threshold)
        self._image_size = int(image_size)
        self._model = None
        self._lock = Lock()

    # ---- accessors -------------------------------------------------------
    @property
    def model_path(self) -> Path:
        return self._model_path

    @property
    def model_version(self) -> str:
        return self._loader.version_of(self._model_path)

    @property
    def labels(self) -> list[str]:
        """Class names the model can predict (loads the model if needed)."""
        return list(self._ensure_model().names.values())

    # ---- behaviour -------------------------------------------------------
    def load(self) -> None:
        """Load the model now (fail fast at start-up instead of on first scan)."""
        self._ensure_model()

    def _ensure_model(self):
        with self._lock:
            if self._model is None:
                self._model = self._loader.load(self._model_path)
            return self._model

    def predict(self, image: Image.Image) -> list[Detection]:
        """Detect waste items in ``image`` (RGB PIL image), best first.

        Raises ``InferenceError`` if the model fails.

        DEBUG: to see raw model output, print ``result.boxes`` below.
        """
        model = self._ensure_model()
        try:
            with self._lock:
                result = model.predict(image, conf=self._min_confidence, imgsz=self._image_size,
                                       device=pick_device(), verbose=False)[0]
            detections = [
                Detection(
                    label=result.names[int(box.cls[0])],
                    confidence=float(box.conf[0]),
                    box=BoundingBox(*[float(v) for v in box.xyxy[0].tolist()]),
                )
                for box in result.boxes
            ]
        except Exception as error:
            raise InferenceError(f"Model prediction failed: {error}") from error
        detections.sort(key=lambda d: d.confidence, reverse=True)
        return detections

    def stream(self, image: Image.Image) -> Iterator[Detection]:
        """Predict and return the detections as an iterator."""
        return DetectionStream(self.predict(image))
