"""Abstract contract shared by every stream processor."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from .events import RecognitionEvent

if TYPE_CHECKING:
    from .pipeline import ProcessingPipeline


class StreamProcessor(ABC):
    """ABC demonstrating a uniform, polymorphic processor API."""

    @abstractmethod
    def process(self, event: RecognitionEvent) -> RecognitionEvent:
        """Transform one recognition event and return the result."""
        raise NotImplementedError

    def __or__(self, other: "StreamProcessor") -> "ProcessingPipeline":
        """Overload | so processors compose as readable pipelines."""
        from .pipeline import ProcessingPipeline

        if not isinstance(other, StreamProcessor):
            return NotImplemented
        return ProcessingPipeline([self, other])
