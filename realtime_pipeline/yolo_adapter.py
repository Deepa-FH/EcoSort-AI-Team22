"""Adapter that isolates Ultralytics YOLO from pipeline classes."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .events import BoundingBox
from .exceptions import ModelLoadError


class YOLOModelAdapter:
    def __init__(self, model_path: str | Path, confidence: float = 0.20) -> None:
        self._model_path = Path(model_path)
        self._confidence = confidence
        self._model: Any = None

    @property
    def model_path(self) -> Path:
        return self._model_path

    def initialize(self) -> None:
        if not self._model_path.exists():
            raise ModelLoadError(f"Model not found: {self._model_path}")
        try:
            from ultralytics import YOLO
            self._model = YOLO(str(self._model_path))
        except Exception as exc:
            raise ModelLoadError(f"Could not load model: {exc}") from exc

    def detect_best(self, frame: Any) -> tuple[str, float, BoundingBox | None, set[str]]:
        if self._model is None:
            self.initialize()
        results = self._model.predict(frame, conf=self._confidence, verbose=False)
        if not results or results[0].boxes is None or len(results[0].boxes) == 0:
            return "Unknown", 0.0, None, {"no-detection"}

        boxes = results[0].boxes
        best_index = int(boxes.conf.argmax().item())
        confidence = float(boxes.conf[best_index].item())
        class_id = int(boxes.cls[best_index].item())
        label = str(results[0].names[class_id])
        x1, y1, x2, y2 = (int(value) for value in boxes.xyxy[best_index].tolist())
        box = BoundingBox(x1, y1, x2, y2)
        tags = self._infer_visual_tags(label, box)
        return label, confidence, box, tags

    @staticmethod
    def _infer_visual_tags(label: str, box: BoundingBox) -> set[str]:
        tags = {label.lower(), "large" if box.area > 100_000 else "small"}
        if box.aspect_ratio > 1.35:
            tags.add("bottle-shaped")
        elif box.aspect_ratio < 0.75:
            tags.add("flat-or-wide")
        else:
            tags.add("compact")
        if label.lower() == "metal":
            tags.add("can-candidate")
        return tags
