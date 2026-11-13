"""Subsystem 2 - AI Image Recognition (owner: Prasad Hule)."""
from .confidence_filter import MAX_THRESHOLD, MIN_THRESHOLD, ConfidenceFilter
from .detection_models import BoundingBox, Detection, PredictionResult
from .detector import DetectionStream, WasteDetector, pick_device
from .exceptions import (InferenceError, InvalidConfidenceError, ModelNotFoundError,
                         RecognitionError, RecognitionErrorHandler)
from .model_evaluator import EvaluationReport, ModelEvaluator
from .model_loader import ModelLoader
from .recognition_service import ImageRecognitionService

__all__ = [
    "BoundingBox", "Detection", "PredictionResult", "ConfidenceFilter", "MIN_THRESHOLD",
    "MAX_THRESHOLD", "ModelLoader", "WasteDetector", "DetectionStream", "pick_device",
    "ImageRecognitionService", "ModelEvaluator", "EvaluationReport", "RecognitionError",
    "ModelNotFoundError", "InvalidConfidenceError", "InferenceError", "RecognitionErrorHandler",
]
