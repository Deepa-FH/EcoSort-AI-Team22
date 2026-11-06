"""Small, dependency-injected versions of Sortly AI subsystem boundaries."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from .dataset_errors import CorruptImageError, EmptyImageError, ImageTooLargeError, UnsupportedImageError
from .recognition_errors import InferenceError, InvalidConfidenceError, ModelNotFoundError
from .recycling_ai_errors import EmptyLLMResponseError, LLMServiceError, MissingAPIKeyError


class ImageValidationService:
    SUPPORTED_FORMATS = {"JPEG", "PNG", "WEBP"}

    def __init__(self, max_bytes: int = 8 * 1024 * 1024) -> None:
        self.max_bytes = max_bytes

    def validate(self, content: bytes) -> Image.Image:
        if not content:
            raise EmptyImageError("No image bytes were supplied")
        if len(content) > self.max_bytes:
            raise ImageTooLargeError(f"Image has {len(content)} bytes; maximum is {self.max_bytes}")
        try:
            image = Image.open(BytesIO(content))
            image.load()
        except (UnidentifiedImageError, OSError) as exc:
            raise CorruptImageError("Pillow could not decode the image") from exc
        if image.format not in self.SUPPORTED_FORMATS:
            raise UnsupportedImageError(f"Unsupported image format: {image.format}")
        return image.convert("RGB")


class RecognitionService:
    def __init__(self, model_path: str | Path, predictor=None, confidence: float = 0.50) -> None:
        self.model_path = Path(model_path)
        self.predictor = predictor
        self.confidence = 0.0
        self.set_confidence(confidence)

    def set_confidence(self, value: float) -> None:
        if not 0 <= value <= 1:
            raise InvalidConfidenceError(f"Invalid confidence: {value}")
        self.confidence = float(value)

    def ensure_model_exists(self) -> None:
        if not self.model_path.is_file():
            raise ModelNotFoundError(f"Model file not found: {self.model_path}")

    def predict(self, image: Image.Image) -> dict:
        if self.predictor is None:
            self.ensure_model_exists()
            return {"label": "Unknown", "confidence": 0.0}
        try:
            return self.predictor(image)
        except Exception as exc:
            raise InferenceError("The predictor raised an exception") from exc


class RecyclingAssistantService:
    def __init__(self, api_key: str | None, llm_client, rules: dict[str, str] | None = None) -> None:
        self.api_key = api_key
        self.llm_client = llm_client
        self.rules = rules or {"paper": "Use the blue paper bin.", "glass": "Use a glass container."}

    def ask_llm(self, material: str) -> str:
        if not self.api_key:
            raise MissingAPIKeyError("No API key was supplied")
        try:
            response = self.llm_client.ask(material)
        except Exception as exc:
            raise LLMServiceError("The external service failed") from exc
        if not response or not str(response).strip():
            raise EmptyLLMResponseError("The external service returned no text")
        return str(response).strip()

    def answer(self, material: str) -> dict:
        local = self.rules.get(material.lower(), "Check the local recycling authority.")
        try:
            return {"source": "llm", "answer": self.ask_llm(material)}
        except (MissingAPIKeyError, LLMServiceError, EmptyLLMResponseError):
            return {"source": "local-fallback", "answer": local}
