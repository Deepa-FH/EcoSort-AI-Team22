"""Prasad Hule: AI Image Recognition error boundary."""
from .common import ErrorResult


class RecognitionError(Exception):
    """Base exception for model setup and inference."""


class ModelNotFoundError(RecognitionError): pass
class ModelLoadError(RecognitionError): pass
class InvalidConfidenceError(RecognitionError): pass
class InferenceError(RecognitionError): pass


class RecognitionErrorHandler:
    subsystem = "AI Image Recognition"
    _mapping = {
        ModelNotFoundError: ("MODEL_NOT_FOUND", "The recognition model is unavailable.", 503, False),
        ModelLoadError: ("MODEL_LOAD_FAILED", "The recognition model could not be loaded.", 503, False),
        InvalidConfidenceError: ("INVALID_CONFIDENCE", "Confidence must be between 0 and 1.", 400, True),
        InferenceError: ("INFERENCE_FAILED", "The image could not be classified.", 500, True),
    }

    def handle(self, error: Exception) -> ErrorResult:
        code, message, status, recoverable = self._mapping.get(type(error), ("RECOGNITION_UNKNOWN", "Recognition failed.", 500, False))
        return ErrorResult(self.subsystem, code, message, status, recoverable)
