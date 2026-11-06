from ..events import RecognitionEvent
from ..stream_processor import StreamProcessor


class ConfidenceFilter(StreamProcessor):
    """Polymorphic processor that marks weak predictions for review."""
    def __init__(self, minimum_confidence: float = 0.50) -> None:
        if not 0 <= minimum_confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1.")
        self.minimum_confidence = minimum_confidence

    def process(self, event: RecognitionEvent) -> RecognitionEvent:
        if event.confidence < self.minimum_confidence:
            return event.clone(accepted=False, material_category="Uncertain material", routing_code="ROUTE_REVIEW_99", status_message="Low confidence - manual review")
        return event.clone(accepted=True, status_message="Confidence accepted")
