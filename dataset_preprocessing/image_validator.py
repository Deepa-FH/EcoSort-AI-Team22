from __future__ import annotations

from io import BytesIO
from PIL import Image, ImageOps, UnidentifiedImageError

from .exceptions import ImageTooLargeError, PreprocessingError, UnsupportedImageError


class ImageValidator:
    """Validate uploads and normalize orientation without saving user photos."""

    allowed_formats = {"JPEG", "PNG", "WEBP"}

    def __init__(self, max_bytes: int = 10 * 1024 * 1024, max_pixels: int = 20_000_000):
        self.max_bytes = max_bytes
        self.max_pixels = max_pixels

    def validate_and_prepare(self, data: bytes) -> Image.Image:
        if not data:
            raise PreprocessingError("The uploaded image is empty.")
        if len(data) > self.max_bytes:
            raise ImageTooLargeError("The image must be smaller than 10 MB.")
        try:
            with Image.open(BytesIO(data)) as source:
                if source.format not in self.allowed_formats:
                    raise UnsupportedImageError("Use a JPG, PNG, or WebP image.")
                if source.width * source.height > self.max_pixels:
                    raise ImageTooLargeError("The image is larger than 20 megapixels.")
                source.load()
                image = ImageOps.exif_transpose(source).convert("RGB")
                image.thumbnail((1600, 1600))
                return image
        except (UnidentifiedImageError, OSError) as error:
            raise PreprocessingError("The uploaded file is not a readable image.") from error
