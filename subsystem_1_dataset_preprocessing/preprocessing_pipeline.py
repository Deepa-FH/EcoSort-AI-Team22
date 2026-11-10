"""Preprocessing steps and the pipeline that chains them.

OOP ideas shown in this file
----------------------------
* ABSTRACT BASE CLASS  - ``ImageStep`` defines the contract (``apply``).
* INHERITANCE          - ``ResizeStep`` and ``RGBStep`` implement the contract.
* POLYMORPHISM         - the pipeline calls ``step.apply(image)`` on every step
                         without caring which concrete class it is.
* COMPOSITE PATTERN    - ``PreprocessingPipeline`` is itself an ``ImageStep``.
* OPERATOR OVERLOADING - ``step_a | step_b`` builds a pipeline (``__or__``).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator

import numpy as np
from PIL import Image


class ImageStep(ABC):
    """Contract for one preprocessing step: image in, image out."""

    @abstractmethod
    def apply(self, image: Image.Image) -> Image.Image:
        """Transform ``image`` and return the result (never modify in place)."""

    def __or__(self, other: "ImageStep") -> "PreprocessingPipeline":
        """``a | b`` creates a pipeline that runs ``a`` and then ``b``."""
        return PreprocessingPipeline([self, other])

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"


class RGBStep(ImageStep):
    """Make sure the image has 3 colour channels (the model expects RGB)."""

    def apply(self, image: Image.Image) -> Image.Image:
        return image.convert("RGB")


class ResizeStep(ImageStep):
    """Shrink the image so its longest side is at most ``max_side`` pixels.

    Small images are NOT enlarged (enlarging adds no information).
    """

    def __init__(self, max_side: int = 2000):
        if max_side <= 0:
            raise ValueError("max_side must be positive")
        self._max_side = int(max_side)

    @property
    def max_side(self) -> int:
        """Longest allowed side in pixels."""
        return self._max_side

    @max_side.setter
    def max_side(self, value: int) -> None:
        if int(value) <= 0:
            raise ValueError("max_side must be positive")
        self._max_side = int(value)

    def apply(self, image: Image.Image) -> Image.Image:
        result = image.copy()
        # thumbnail() keeps the aspect ratio and only ever shrinks.
        result.thumbnail((self._max_side, self._max_side), Image.Resampling.LANCZOS)
        return result

    def __repr__(self) -> str:
        return f"ResizeStep(max_side={self._max_side})"


class PreprocessingPipeline(ImageStep):
    """An ordered list of ``ImageStep`` objects that is also an ``ImageStep``."""

    def __init__(self, steps: list[ImageStep] | None = None):
        self._steps: list[ImageStep] = list(steps or [])

    @classmethod
    def default(cls, max_side: int = 2000) -> "PreprocessingPipeline":
        """The pipeline used by the web app: convert to RGB, then resize."""
        return cls([RGBStep(), ResizeStep(max_side)])

    # ---- container behaviour (special methods) -------------------------
    def __or__(self, other: ImageStep) -> "PreprocessingPipeline":
        """``pipeline | step`` appends a step (returns a new pipeline)."""
        return PreprocessingPipeline(self._steps + [other])

    def __len__(self) -> int:
        return len(self._steps)

    def __iter__(self) -> Iterator[ImageStep]:
        return iter(self._steps)

    def __repr__(self) -> str:
        return "PreprocessingPipeline([" + ", ".join(repr(s) for s in self._steps) + "])"

    # ---- main behaviour ------------------------------------------------
    @property
    def steps(self) -> list[ImageStep]:
        """A copy of the step list (callers cannot break the pipeline)."""
        return list(self._steps)

    def apply(self, image: Image.Image) -> Image.Image:
        """Run every step in order. Polymorphism: each step decides what to do."""
        for step in self._steps:
            image = step.apply(image)
        return image

    @staticmethod
    def to_normalized_array(image: Image.Image) -> np.ndarray:
        """Return pixels scaled to 0..1 as a float32 array (height, width, 3).

        YOLO normalises internally, so the web app does not need this; it is
        the "normalize pixel values" requirement of the PPT and is used for
        dataset work.
        """
        return np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0
