"""Deepa Halapeti: Dataset and Preprocessing error boundary."""
from .common import ErrorResult


class DatasetError(Exception):
    """Base exception for unsafe or invalid image input."""


class EmptyImageError(DatasetError): pass
class UnsupportedImageError(DatasetError): pass
class CorruptImageError(DatasetError): pass
class ImageTooLargeError(DatasetError): pass


class DatasetErrorHandler:
    subsystem = "Dataset and Preprocessing"
    _mapping = {
        EmptyImageError: ("DATASET_EMPTY", "The uploaded image is empty.", 400),
        UnsupportedImageError: ("DATASET_FORMAT", "Use a JPG, PNG, or WEBP image.", 400),
        CorruptImageError: ("DATASET_CORRUPT", "The uploaded image could not be read.", 400),
        ImageTooLargeError: ("DATASET_TOO_LARGE", "The uploaded image is too large.", 413),
    }

    def handle(self, error: Exception) -> ErrorResult:
        code, message, status = self._mapping.get(type(error), ("DATASET_UNKNOWN", "Image preprocessing failed.", 500))
        return ErrorResult(self.subsystem, code, message, status, status < 500)
