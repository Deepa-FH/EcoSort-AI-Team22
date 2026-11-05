from ..events import RecognitionEvent
from ..stream_processor import StreamProcessor


class FrameAnnotator(StreamProcessor):
    """Draws the processed event on its video frame."""
    def process(self, event: RecognitionEvent) -> RecognitionEvent:
        import cv2
        frame = event.frame.copy()
        color = (31, 139, 86) if event.accepted else (40, 40, 220)
        if event.bounding_box is not None:
            box = event.bounding_box
            cv2.rectangle(frame, (box.x1, box.y1), (box.x2, box.y2), color, 3)
        overlay = frame.copy()
        cv2.rectangle(overlay, (12, 12), (610, 142), (20, 35, 29), -1)
        cv2.addWeighted(overlay, 0.82, frame, 0.18, 0, frame)
        lines = [
            f"Frame {event.frame_number} | {event.timestamp_seconds:05.2f}s",
            f"Prediction: {event.model_label} ({event.confidence:.1%})",
            f"Material: {event.material_category}",
            f"Route: {event.routing_code}",
            event.status_message,
        ]
        for index, text in enumerate(lines):
            cv2.putText(frame, text, (28, 38 + index * 23), cv2.FONT_HERSHEY_SIMPLEX, 0.60, (240, 250, 245), 2, cv2.LINE_AA)
        return event.clone(frame=frame)
