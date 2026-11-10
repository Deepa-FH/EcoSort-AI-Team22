"""Subsystem 2 - exceptions and error handler (owner: Prasad Hule).

    EcoSortError
      +-- RecognitionError
            +-- ModelNotFoundError     (weights file missing / not a detector)
            +-- InvalidConfidenceError (threshold outside the allowed range)
            +-- InferenceError         (the model crashed while predicting)
"""

from shared.error_handling import BaseErrorHandler, EcoSortError


class RecognitionError(EcoSortError):
    """Base class for model loading and inference problems."""

    code = "RECOGNITION_ERROR"
    safe_message = "The image could not be analysed."
    http_status = 500


class ModelNotFoundError(RecognitionError):
    """The trained model file does not exist or has the wrong type."""

    code = "MODEL_NOT_FOUND"
    safe_message = "The recognition model is not available on the server."


class InvalidConfidenceError(RecognitionError):
    """A confidence threshold outside (0, 1]."""

    code = "INVALID_CONFIDENCE"
    safe_message = "The confidence threshold must be between 0 and 1."
    http_status = 400
    recoverable = True


class InferenceError(RecognitionError):
    """The model raised an error while predicting."""

    code = "INFERENCE_FAILED"
    safe_message = "The model could not analyse this image. Please try another photo."
    recoverable = True


class RecognitionErrorHandler(BaseErrorHandler):
    """Error handler of Subsystem 2 (logic inherited from ``BaseErrorHandler``)."""

    subsystem = "image_recognition"
