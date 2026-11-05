"""Subsystem 2: Prasad Hule — AI Image Recognition."""
from .model_loader import ModelLoader
from .detection_models import BoundingBox, DetectionResult
from .confidence_filter import ConfidenceFilter
from .waste_detector import WasteDetector

__all__ = ["ModelLoader", "BoundingBox", "DetectionResult", "ConfidenceFilter", "WasteDetector"]
