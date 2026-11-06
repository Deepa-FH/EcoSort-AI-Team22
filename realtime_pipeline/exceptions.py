class StreamProcessingError(RuntimeError):
    """Base exception for real-time stream failures."""


class VideoOpenError(StreamProcessingError):
    """Raised when a video source cannot be opened."""


class ModelLoadError(StreamProcessingError):
    """Raised when the local YOLO model cannot be loaded."""
