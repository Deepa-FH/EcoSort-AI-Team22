"""ModelLoader - loads the trained YOLO weights once and remembers them."""

from __future__ import annotations

from pathlib import Path

from .exceptions import ModelNotFoundError


class ModelLoader:
    """Loads (and caches) YOLO models.

    Keeping loading in its own class means the detector can be tested with a
    fake loader - no 5 MB weights file and no GPU needed (DEPENDENCY INJECTION).
    """

    def __init__(self):
        self._cache: dict[str, object] = {}

    def load(self, model_path: Path | str):
        """Return the YOLO model stored at ``model_path``.

        Raises ``ModelNotFoundError`` when the file is missing, cannot be read
        or is not an object-detection model.

        DEBUG: the first call takes a few seconds (importing ultralytics and
        reading the weights); later calls come from the cache.
        """
        path = Path(model_path)
        if not path.is_file():
            raise ModelNotFoundError(f"Model file not found: {path}")
        key = str(path.resolve())
        if key not in self._cache:
            try:
                from ultralytics import YOLO       # heavy import, so only when needed
                model = YOLO(str(path))
            except Exception as error:             # any loader failure -> one clear error
                raise ModelNotFoundError(f"Could not read model {path}: {error}") from error
            if getattr(model, "task", "detect") != "detect":
                raise ModelNotFoundError("The supplied model is not an object-detection model.")
            self._cache[key] = model
        return self._cache[key]

    @staticmethod
    def version_of(model_path: Path | str) -> str:
        """Model identity shown in results, e.g. ``best_model.pt (5.2 MB)``."""
        path = Path(model_path)
        size = f"{path.stat().st_size / 1_048_576:.1f} MB" if path.is_file() else "missing"
        return f"{path.name} ({size})"
