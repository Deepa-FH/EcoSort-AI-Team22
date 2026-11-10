"""ImageValidator - the gatekeeper for every image entering the system.

Used by the web app on each upload (so it runs in the real application, not
only in tests).
"""

from __future__ import annotations

from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError

from .exceptions import (CorruptImageError, EmptyImageError, ImageTooLargeError,
                         ImageTooSmallError, UnsupportedImageError)


class ImageValidator:
    """Checks an uploaded image and returns a clean RGB ``PIL.Image``.

    OOP idea: ENCAPSULATION. The limits are stored in private attributes
    (``_max_bytes`` ...) and can only be changed through properties that
    validate the new value.
    """

    #: Image formats the system accepts (class attribute, shared by all objects).
    ALLOWED_FORMATS = frozenset({"JPEG", "PNG", "WEBP"})

    def __init__(self, max_bytes: int = 8 * 1024 * 1024,
                 max_pixels: int = 20_000_000, min_side: int = 80):
        # Going through the property setters makes the validation run in __init__ too.
        self.max_bytes = max_bytes
        self.max_pixels = max_pixels
        self.min_side = min_side

    # ---- getters / setters (properties) ---------------------------------
    @property
    def max_bytes(self) -> int:
        """Maximum accepted file size in bytes."""
        return self._max_bytes

    @max_bytes.setter
    def max_bytes(self, value: int) -> None:
        if int(value) <= 0:
            raise ValueError("max_bytes must be positive")
        self._max_bytes = int(value)

    @property
    def max_pixels(self) -> int:
        """Maximum accepted width*height (protects memory)."""
        return self._max_pixels

    @max_pixels.setter
    def max_pixels(self, value: int) -> None:
        if int(value) <= 0:
            raise ValueError("max_pixels must be positive")
        self._max_pixels = int(value)

    @property
    def min_side(self) -> int:
        """Smallest accepted width or height in pixels."""
        return self._min_side

    @min_side.setter
    def min_side(self, value: int) -> None:
        if int(value) < 1:
            raise ValueError("min_side must be at least 1")
        self._min_side = int(value)

    # ---- behaviour -------------------------------------------------------
    def validate_and_prepare(self, data: bytes) -> Image.Image:
        """Validate raw upload bytes and return an upright RGB image.

        Raises one of the specific ``PreprocessingError`` subclasses, so the
        caller (and the error handler) knows exactly what went wrong.

        DEBUG: if a perfectly good photo is rejected, print ``source.format``
        and ``source.size`` inside the ``with`` block below.
        """
        if not data:
            raise EmptyImageError("Upload contained 0 bytes")
        if len(data) > self._max_bytes:
            raise ImageTooLargeError(f"{len(data)} bytes > limit {self._max_bytes}")
        try:
            with Image.open(BytesIO(data)) as source:
                if source.format not in self.ALLOWED_FORMATS:
                    raise UnsupportedImageError(f"format {source.format!r} not allowed")
                width, height = source.size
                if width * height > self._max_pixels:
                    raise ImageTooLargeError(f"{width}x{height} exceeds pixel limit")
                if min(width, height) < self._min_side:
                    raise ImageTooSmallError(f"{width}x{height} below {self._min_side}px")
                source.load()  # force a real decode so truncated files fail here
                # exif_transpose rotates phone photos to the correct orientation.
                return ImageOps.exif_transpose(source).convert("RGB")
        except (UnidentifiedImageError, OSError, SyntaxError, ValueError) as error:
            # "raise ... from error" keeps the original cause for the server log.
            raise CorruptImageError(f"Pillow could not decode the data: {error}") from error

    def __repr__(self) -> str:
        return (f"ImageValidator(max_bytes={self._max_bytes}, "
                f"max_pixels={self._max_pixels}, min_side={self._min_side})")
