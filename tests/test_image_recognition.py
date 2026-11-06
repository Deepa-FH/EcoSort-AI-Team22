from pathlib import Path

import pytest
from PIL import Image

from ecosort_testing.recognition_errors import InferenceError, InvalidConfidenceError, ModelNotFoundError, RecognitionErrorHandler
from ecosort_testing.sample_services import RecognitionService


def test_05_valid_confidence_is_accepted():
    service = RecognitionService("unused.pt", predictor=lambda image: {"label": "Paper"}, confidence=0.75)
    assert service.confidence == 0.75


def test_06_invalid_confidence_raises_specific_error():
    with pytest.raises(InvalidConfidenceError):
        RecognitionService("unused.pt", confidence=1.10)


def test_07_missing_model_file_raises_specific_error():
    with pytest.raises(ModelNotFoundError):
        RecognitionService(Path("definitely_missing_model_file.pt")).ensure_model_exists()


def test_08_predictor_failure_is_chained_as_inference_error():
    def broken_predictor(image):
        raise RuntimeError("GPU detail that must not reach the user")
    service = RecognitionService("unused.pt", predictor=broken_predictor)
    with pytest.raises(InferenceError) as captured:
        service.predict(Image.new("RGB", (2, 2)))
    assert isinstance(captured.value.__cause__, RuntimeError)
    result = RecognitionErrorHandler().handle(captured.value)
    assert result.code == "INFERENCE_FAILED" and "GPU" not in result.message
