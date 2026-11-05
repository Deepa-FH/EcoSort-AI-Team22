from __future__ import annotations

from abc import ABC, abstractmethod
from PIL import Image


class ImageStep(ABC):
    @abstractmethod
    def apply(self, image: Image.Image) -> Image.Image: ...

    def __or__(self, other: "ImageStep") -> "PreprocessingPipeline":
        return PreprocessingPipeline([self, other])


class ResizeStep(ImageStep):
    def __init__(self, size: tuple[int, int] = (640, 640)):
        self.size = size

    def apply(self, image: Image.Image) -> Image.Image:
        result = image.copy()
        result.thumbnail(self.size)
        return result


class RGBStep(ImageStep):
    def apply(self, image: Image.Image) -> Image.Image:
        return image.convert("RGB")


class PreprocessingPipeline(ImageStep):
    def __init__(self, steps: list[ImageStep]):
        self.steps = steps

    def __or__(self, other: ImageStep) -> "PreprocessingPipeline":
        return PreprocessingPipeline(self.steps + [other])

    def apply(self, image: Image.Image) -> Image.Image:
        for step in self.steps:
            image = step.apply(image)
        return image
