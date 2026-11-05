from pathlib import Path


class ImageLoader:
    """Loads supported image input; owned by Deepa Halapeti."""
    def __init__(self, allowed_extensions: set[str] | None = None) -> None:
        self._allowed_extensions = allowed_extensions or {".jpg", ".jpeg", ".png"}
        self._initialized = False

    def initialize(self) -> None:
        self._initialized = True

    def get_allowed_extensions(self) -> set[str]:
        return set(self._allowed_extensions)

    def set_allowed_extensions(self, extensions: set[str]) -> None:
        if not extensions:
            raise ValueError("At least one extension is required.")
        self._allowed_extensions = {item.lower() for item in extensions}

    def load(self, filename: str, content: bytes) -> bytes:
        if Path(filename).suffix.lower() not in self._allowed_extensions:
            raise ValueError("Unsupported image extension.")
        if not content:
            raise ValueError("Image content is empty.")
        return content
