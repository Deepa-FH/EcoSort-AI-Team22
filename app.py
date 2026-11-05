from exceptions import DatasetError, RecognitionError, RecyclingAIError, DashboardError

def parse_image(name):
    if not name: raise DatasetError("image is required")
    if not name.lower().endswith((".jpg",".jpeg",".png",".webp")): raise DatasetError("unsupported image")
    return True
def check_confidence(value):
    if not 0 < value <= 1: raise RecognitionError("invalid confidence")
    return value
def ask_service(api_key):
    if not api_key: raise RecyclingAIError("missing API key")
    return "answer"
def validate_material(material):
    if not material: raise DashboardError("material is required")
    return material.strip()
