class RecognitionError(Exception):
    """Base error for model loading and inference."""


class ModelNotFoundError(RecognitionError):
    pass


class InvalidConfidenceError(RecognitionError):
    pass
