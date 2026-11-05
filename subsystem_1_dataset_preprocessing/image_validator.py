class ImageValidator:
    """Validates upload size and content; owned by Deepa Halapeti."""
    def __init__(self, max_size_mb: float = 8.0) -> None:
        self._max_size_mb = 0.0
        self.set_max_size_mb(max_size_mb)

    def initialize(self, max_size_mb: float | None = None) -> None:
        if max_size_mb is not None:
            self.set_max_size_mb(max_size_mb)

    def get_max_size_mb(self) -> float:
        return self._max_size_mb

    def set_max_size_mb(self, value: float) -> None:
        if value <= 0:
            raise ValueError("Maximum size must be positive.")
        self._max_size_mb = float(value)

    def validate(self, content: bytes) -> bool:
        if not content:
            raise ValueError("Image is empty.")
        if len(content) > self._max_size_mb * 1024 * 1024:
            raise ValueError("Image exceeds the maximum size.")
        return True
