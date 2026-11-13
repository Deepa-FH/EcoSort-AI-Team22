"""ImageLoader - reads dataset images from disk (used for dataset work and demos)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from .exceptions import CorruptImageError, DatasetError


class ImageLoader:
    """Loads a single image file and converts it to RGB."""

    def load(self, path: Path | str) -> Image.Image:
        """Open ``path`` and return it as an RGB image.

        Raises:
            DatasetError: the file does not exist.
            CorruptImageError: the file exists but is not a readable image.
        """
        path = Path(path)
        if not path.is_file():
            raise DatasetError(f"Image not found: {path}")
        try:
            with Image.open(path) as image:
                return image.convert("RGB")
        except OSError as error:
            raise CorruptImageError(f"Cannot open image: {path}") from error

    def load_bytes(self, path: Path | str) -> bytes:
        """Return the raw bytes of a file (used to feed ``ImageValidator``)."""
        path = Path(path)
        if not path.is_file():
            raise DatasetError(f"Image not found: {path}")
        return path.read_bytes()
