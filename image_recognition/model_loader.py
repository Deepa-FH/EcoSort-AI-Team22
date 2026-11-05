from pathlib import Path
from .exceptions import ModelNotFoundError


class ModelLoader:
    def load(self, model_path: Path):
        if not model_path.is_file():
            raise ModelNotFoundError(f"Model not found: {model_path}")
        from ultralytics import YOLO
        model = YOLO(str(model_path))
        if model.task != "detect":
            raise ModelNotFoundError("The supplied model is not an object-detection model.")
        return model
