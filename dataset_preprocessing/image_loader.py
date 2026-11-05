from pathlib import Path
from PIL import Image

from .exceptions import PreprocessingError


class ImageLoader:
    """Load local dataset images for training or demonstration."""

    def load(self, path: Path) -> Image.Image:
        if not path.is_file():
            raise PreprocessingError(f"Image not found: {path}")
        try:
            with Image.open(path) as image:
                return image.convert("RGB")
        except OSError as error:
            raise PreprocessingError(f"Cannot open image: {path}") from error
