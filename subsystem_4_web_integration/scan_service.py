"""ScanService - the "scan a photo" use case (this is where subsystems 1, 2 and 3 meet)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from pathlib import Path

from subsystem_1_dataset_preprocessing import ImageValidator, PreprocessingPipeline
from subsystem_2_image_recognition import ImageRecognitionService, PredictionResult
from subsystem_3_recycling_ai import RecyclingRuleEngine

from .exceptions import StorageError
from .waste_repository import WasteRepository

PHOTO_PREFIX = "web_"      # all stored photos are called web_<random>.jpg


def is_valid_photo_name(name: str) -> bool:
    """Only accept our own file names (blocks path tricks like ``../secret``)."""
    return name == Path(name).name and name.startswith(PHOTO_PREFIX) and name.endswith(".jpg")


@dataclass
class ScanOutcome:
    """What ``ScanService.analyze`` returns to the controller."""

    response: dict               # JSON sent to the browser
    prediction: PredictionResult
    image_path: Path
    scan_id: int


class ScanService:
    """Validate -> preprocess -> store photo -> recognise -> save scan."""

    def __init__(self, validator: ImageValidator, pipeline: PreprocessingPipeline,
                 recognition: ImageRecognitionService, rules: RecyclingRuleEngine,
                 repository: WasteRepository, capture_dir: Path):
        self._validator = validator          # Subsystem 1
        self._pipeline = pipeline            # Subsystem 1
        self._recognition = recognition      # Subsystem 2
        self._rules = rules                  # Subsystem 3
        self._repository = repository        # Subsystem 4
        self._capture_dir = Path(capture_dir)

    @property
    def capture_dir(self) -> Path:
        return self._capture_dir

    def warm_up(self) -> None:
        """Ask Subsystem 2 to load its model now."""
        self._recognition.start()

    def analyze(self, image_bytes: bytes, threshold_percent: float, user_id: int | None) -> ScanOutcome:
        """Run the complete scan workflow for one uploaded photo.

        Raises subsystem-specific errors (``PreprocessingError``, ``InferenceError``,
        ``StorageError``); the web app turns them into safe JSON answers.

        DEBUG: to follow a scan, print after each numbered step below.
        """
        image = self._validator.validate_and_prepare(image_bytes)          # 1. Subsystem 1: check
        image = self._pipeline.apply(image)                                # 2. Subsystem 1: RGB + resize

        self._capture_dir.mkdir(parents=True, exist_ok=True)               # 3. keep the photo for history
        image_path = self._capture_dir / f"{PHOTO_PREFIX}{uuid.uuid4().hex}.jpg"
        try:
            image.save(image_path, format="JPEG", quality=90)
        except OSError as error:
            raise StorageError(f"Could not write {image_path}: {error}") from error

        prediction = self._recognition.recognize(image, threshold_percent) # 4. Subsystem 2: YOLO
        top = prediction.top
        rule = self._rules.get(top.label) if top else None                 # 5. Subsystem 3: bin rule
        scan_id = self._repository.add_scan(                               # 6. Subsystem 4: history
            user_id, f"camera_captures/{image_path.name}",
            top.label if top else None, top.confidence if top else None,
            top.label if top else None, source="local", llm_used=0, llm_tokens=0)

        response = {
            "photo_url": f"/api/photo/{image_path.name}",
            **prediction.to_dict(),
            "route": rule.to_dict() if rule else None,
            "scan_id": scan_id,
        }
        return ScanOutcome(response, prediction, image_path, scan_id)
