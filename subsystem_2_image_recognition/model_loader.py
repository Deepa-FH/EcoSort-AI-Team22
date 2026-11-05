from collections.abc import Callable

class ModelLoader:
    """Loads an injected model without coupling the assignment to YOLO; owned by Prasad Hule."""
    def __init__(self, model_path: str = "models/best_model.pt") -> None:
        self._model_path, self._model = model_path, None
    def initialize(self, factory: Callable[[str], object]) -> object:
        self._model = factory(self._model_path); return self._model
    def get_model_path(self) -> str: return self._model_path
    def set_model_path(self, value: str) -> None:
        if not value.strip(): raise ValueError("Model path cannot be empty.")
        self._model_path = value
    def get_model(self) -> object | None: return self._model
