from ..events import RecognitionEvent
from ..stream_processor import StreamProcessor


class ConveyorRouteAssigner(StreamProcessor):
    """Assigns a conveyor actuator code to the mapped material."""
    ROUTES = {
        "PET candidate": "ROUTE_PLASTIC_01",
        "HDPE candidate": "ROUTE_PLASTIC_02",
        "Aluminum candidate": "ROUTE_METAL_01",
        "Mixed metal": "ROUTE_METAL_02",
        "Container glass": "ROUTE_GLASS_01",
        "Paper": "ROUTE_PAPER_01",
        "Cardboard": "ROUTE_PAPER_02",
        "Organic waste": "ROUTE_ORGANIC_01",
        "Textile": "ROUTE_TEXTILE_01",
        "Residual waste": "ROUTE_RESIDUAL_01",
        "Special waste": "ROUTE_HAZARDOUS_01",
    }

    def process(self, event: RecognitionEvent) -> RecognitionEvent:
        if not event.accepted:
            return event
        route = self.ROUTES.get(event.material_category, "ROUTE_REVIEW_99")
        return event.clone(routing_code=route, status_message="Route assigned" if route != "ROUTE_REVIEW_99" else "Unknown - manual review")
