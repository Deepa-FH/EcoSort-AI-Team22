"""Custom iterator that consumes video frames and emits events."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .events import RecognitionEvent
from .exceptions import VideoOpenError
from .yolo_adapter import YOLOModelAdapter


class VideoEventStream:
    def __init__(self, video_path: str | Path, detector: YOLOModelAdapter, frame_skip: int = 0) -> None:
        self._video_path = Path(video_path)
        self._detector = detector
        self._frame_skip = max(0, frame_skip)
        self._capture: Any = None
        self._frame_number = 0
        self._fps = 20.0

    @property
    def fps(self) -> float:
        return self._fps

    @property
    def frame_size(self) -> tuple[int, int]:
        import cv2
        return int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def initialize(self) -> None:
        import cv2
        self._capture = cv2.VideoCapture(str(self._video_path))
        if not self._capture.isOpened():
            raise VideoOpenError(f"Could not open video: {self._video_path}")
        self._fps = self._capture.get(cv2.CAP_PROP_FPS) or 20.0

    def __iter__(self) -> "VideoEventStream":
        if self._capture is None:
            self.initialize()
        return self

    def __next__(self) -> RecognitionEvent:
        if self._capture is None:
            self.initialize()
        for _ in range(self._frame_skip + 1):
            ok, frame = self._capture.read()
            if not ok:
                self.close()
                raise StopIteration
            self._frame_number += 1
        label, confidence, box, tags = self._detector.detect_best(frame)
        return RecognitionEvent(
            frame_number=self._frame_number,
            timestamp_seconds=self._frame_number / self._fps,
            frame=frame,
            model_label=label,
            confidence=confidence,
            bounding_box=box,
            visual_tags=tags,
        )

    def close(self) -> None:
        if self._capture is not None:
            self._capture.release()
            self._capture = None

    def __enter__(self) -> "VideoEventStream":
        self.initialize()
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
