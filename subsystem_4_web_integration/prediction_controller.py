class PredictionController:
    """Coordinates the classification use case; owned by Vijay Kathiresan."""
    def __init__(self, loader, validator, pipeline, detector, assistant) -> None:
        self._loader, self._validator, self._pipeline = loader, validator, pipeline
        self._detector, self._assistant = detector, assistant
    def initialize(self) -> None: self._loader.initialize()
    def get_detector(self): return self._detector
    def set_detector(self, value) -> None:
        if value is None: raise ValueError("Detector is required.")
        self._detector = value
    def classify(self, filename: str, content: bytes) -> dict:
        loaded = self._loader.load(filename, content); self._validator.validate(loaded)
        result = self._detector.predict(self._pipeline.run(loaded))
        return {"category": result.get_label(), "confidence": result.get_confidence(), **self._assistant.get_guidance(result.get_label())}
