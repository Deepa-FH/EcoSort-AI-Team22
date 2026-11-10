"""Subsystem 1 - exceptions and the error handler (owner: Deepa Halapeti).

Hierarchy (inheritance):

    EcoSortError                      (shared root)
      +-- PreprocessingError          (base of this subsystem)
            +-- EmptyImageError
            +-- UnsupportedImageError
            +-- CorruptImageError
            +-- ImageTooLargeError
            +-- ImageTooSmallError
            +-- DatasetError
"""

from shared.error_handling import BaseErrorHandler, EcoSortError


class PreprocessingError(EcoSortError):
    """Base class: anything wrong with an image or the dataset."""

    code = "PREPROCESSING_ERROR"
    safe_message = "The image could not be processed."
    http_status = 400
    recoverable = True


class EmptyImageError(PreprocessingError):
    """The upload contained no bytes."""

    code = "EMPTY_IMAGE"
    safe_message = "The uploaded image is empty. Please choose another photo."


class UnsupportedImageError(PreprocessingError):
    """The file is an image, but not JPEG / PNG / WebP."""

    code = "UNSUPPORTED_IMAGE"
    safe_message = "Use a JPG, PNG or WebP image."


class CorruptImageError(PreprocessingError):
    """The bytes are not a readable image at all."""

    code = "CORRUPT_IMAGE"
    safe_message = "The image could not be read. Please take another photo."


class ImageTooLargeError(PreprocessingError):
    """The file or its pixel count exceeds the configured limit."""

    code = "IMAGE_TOO_LARGE"
    safe_message = "The image is too large. Please use an image under 8 MB."
    http_status = 413


class ImageTooSmallError(PreprocessingError):
    """The picture is so small the model cannot see anything."""

    code = "IMAGE_TOO_SMALL"
    safe_message = "The image is too small. Please take another photo."


class DatasetError(PreprocessingError):
    """The dataset folder is missing, empty or inconsistent."""

    code = "DATASET_ERROR"
    safe_message = "The dataset could not be loaded."
    http_status = 500
    recoverable = False


class DatasetErrorHandler(BaseErrorHandler):
    """Error handler of Subsystem 1 (all logic is inherited)."""

    subsystem = "dataset_preprocessing"
