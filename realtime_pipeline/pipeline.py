"""Composable pipeline and event generator."""
from __future__ import annotations

from collections.abc import Iterable, Iterator

from .events import RecognitionEvent
from .stream_processor import StreamProcessor


class ProcessingPipeline(StreamProcessor):
    def __init__(self, processors: list[StreamProcessor] | None = None) -> None:
        self._processors = list(processors or [])

    @property
    def processors(self) -> tuple[StreamProcessor, ...]:
        return tuple(self._processors)

    def process(self, event: RecognitionEvent) -> RecognitionEvent:
        current = event
        for processor in self._processors:
            current = processor.process(current)
        return current

    def __or__(self, other: StreamProcessor) -> "ProcessingPipeline":
        if not isinstance(other, StreamProcessor):
            return NotImplemented
        if isinstance(other, ProcessingPipeline):
            return ProcessingPipeline([*self._processors, *other.processors])
        return ProcessingPipeline([*self._processors, other])


def processed_events(stream: Iterable[RecognitionEvent], pipeline: StreamProcessor) -> Iterator[RecognitionEvent]:
    """Generator: lazily process one event at a time."""
    for event in stream:
        yield pipeline.process(event)
