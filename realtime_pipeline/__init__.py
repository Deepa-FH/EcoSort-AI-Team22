"""Real-time stream-processing framework for EcoSort AI."""
from .events import BoundingBox, RecognitionEvent
from .pipeline import ProcessingPipeline, processed_events
from .stream_processor import StreamProcessor
from .video_stream import VideoEventStream
from .yolo_adapter import YOLOModelAdapter

__all__ = ["BoundingBox", "RecognitionEvent", "ProcessingPipeline", "StreamProcessor", "VideoEventStream", "YOLOModelAdapter", "processed_events"]
