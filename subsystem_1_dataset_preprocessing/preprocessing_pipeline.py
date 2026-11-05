class ImagePreprocessor:
    """Describes deterministic image transformation; owned by Deepa Halapeti."""
    def __init__(self, target_size: tuple[int, int] = (640, 640), normalize: bool = True) -> None:
        self._target_size = target_size
        self._normalize = normalize

    def initialize(self) -> None:
        if min(self._target_size) <= 0:
            raise ValueError("Target dimensions must be positive.")

    def get_target_size(self) -> tuple[int, int]:
        return self._target_size

    def set_target_size(self, value: tuple[int, int]) -> None:
        if len(value) != 2 or min(value) <= 0:
            raise ValueError("Target size must contain two positive values.")
        self._target_size = value

    def get_normalize(self) -> bool:
        return self._normalize

    def set_normalize(self, value: bool) -> None:
        self._normalize = bool(value)

    def process(self, content: bytes) -> dict:
        return {"content": content, "size": self._target_size, "normalized": self._normalize}


class PreprocessingPipeline:
    """Coordinates preprocessing operations; owned by Deepa Halapeti."""
    def __init__(self, target_size: tuple[int, int] = (640, 640)) -> None:
        self._processor = ImagePreprocessor(target_size)
        self._initialized = False

    def initialize(self) -> None:
        self._processor.initialize()
        self._initialized = True

    def get_processor(self) -> ImagePreprocessor:
        return self._processor

    def set_processor(self, processor: ImagePreprocessor) -> None:
        if not isinstance(processor, ImagePreprocessor):
            raise TypeError("processor must be an ImagePreprocessor.")
        self._processor = processor

    def run(self, content: bytes) -> dict:
        if not self._initialized:
            self.initialize()
        return self._processor.process(content)
