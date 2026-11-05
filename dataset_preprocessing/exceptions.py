class PreprocessingError(Exception):
    """Base error for invalid or unsafe image input."""


class UnsupportedImageError(PreprocessingError):
    pass


class ImageTooLargeError(PreprocessingError):
    pass
