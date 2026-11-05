from ..events import RecognitionEvent
from ..stream_processor import StreamProcessor


class MaterialCategoryMapper(StreamProcessor):
    """Transforms model labels and visual metrics into material categories."""
    BASE_MAPPING = {
        "glass": "Container glass",
        "papier": "Paper",
        "cardboard": "Cardboard",
        "biomuell": "Organic waste",
        "textile_trash": "Textile",
        "restmuell": "Residual waste",
        "sondermuell": "Special waste",
    }

    def process(self, event: RecognitionEvent) -> RecognitionEvent:
        if not event.accepted:
            return event
        label = event.model_label.lower()
        if label == "plastic":
            material = "PET candidate" if "bottle-shaped" in event.visual_tags else "HDPE candidate"
        elif label == "metal":
            material = "Aluminum candidate" if "can-candidate" in event.visual_tags else "Mixed metal"
        else:
            material = self.BASE_MAPPING.get(label, "Unknown material")
        return event.clone(material_category=material, status_message="Material mapped")
