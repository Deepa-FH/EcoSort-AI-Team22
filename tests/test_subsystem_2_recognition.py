"""Tests for Subsystem 2 - AI Image Recognition (Prasad)."""

import pytest
from PIL import Image

from conftest import FakeDetector
from subsystem_2_image_recognition import (BoundingBox, ConfidenceFilter, Detection, DetectionStream,
                                           ImageRecognitionService, InferenceError, InvalidConfidenceError,
                                           ModelEvaluator, ModelLoader, ModelNotFoundError, PredictionResult,
                                           RecognitionErrorHandler, WasteDetector)


def det(label="Glass", conf=0.8):
    return Detection(label, conf, BoundingBox(0, 0, 10, 10))


def test_detection_percentage_and_box():
    assert det(conf=0.753).confidence_percent == 75.3
    assert BoundingBox(0.04, 1, 2, 3).as_list() == [0.0, 1, 2, 3]


def test_confidence_filter_keeps_only_reliable():
    kept = list(ConfidenceFilter(0.5).filter([det(conf=0.4), det(conf=0.6)]))
    assert len(kept) == 1


def test_threshold_must_be_valid():
    with pytest.raises(InvalidConfidenceError):
        ConfidenceFilter(0)


def test_from_percent_is_clamped_like_the_slider():
    assert ConfidenceFilter.from_percent(5).threshold == 0.10
    assert ConfidenceFilter.from_percent(99).threshold == 0.95


def test_prediction_result_review_flag():
    assert PredictionResult((det(conf=0.4),), threshold=0.5).needs_review is True
    assert PredictionResult((det(conf=0.7),), threshold=0.5).needs_review is False
    assert PredictionResult((), threshold=0.5).needs_review is True        # nothing found


def test_detection_stream_is_an_iterator():
    assert [d.label for d in DetectionStream([det("A"), det("B")])] == ["A", "B"]


def test_missing_model_file(tmp_path):
    with pytest.raises(ModelNotFoundError):
        ModelLoader().load(tmp_path / "missing.pt")


def test_inference_failure_is_wrapped():
    class BrokenModel:
        names = {0: "x"}
        def predict(self, *a, **k): raise RuntimeError("gpu exploded")
    class FakeLoader(ModelLoader):
        def load(self, path): return BrokenModel()
    with pytest.raises(InferenceError) as info:
        WasteDetector("any.pt", loader=FakeLoader()).predict(Image.new("RGB", (10, 10)))
    assert isinstance(info.value.__cause__, RuntimeError)      # original error kept ("raise from")


def test_service_sorts_and_flags_low_confidence():
    service = ImageRecognitionService(FakeDetector("Metal", 0.4))
    result = service.recognize(Image.new("RGB", (30, 20)), threshold_percent=50)
    assert result.top.label == "Metal" and result.needs_review and result.image_size == (30, 20)


def test_evaluator_computes_metrics():
    report = ModelEvaluator().evaluate([("a", "a"), ("a", "b"), ("b", "b"), ("b", "b")])
    assert report.accuracy == 0.75
    assert report.per_class["b"]["recall"] == 1.0 and report.per_class["b"]["precision"] == pytest.approx(2 / 3)


def test_error_handler_marks_model_error_unrecoverable():
    response = RecognitionErrorHandler().handle(ModelNotFoundError("C:/private/path.pt"))
    assert response.recoverable is False and "private" not in response.message
