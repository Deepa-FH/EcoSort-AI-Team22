"""Tests for Subsystem 1 - Dataset & Preprocessing (Deepa)."""

import pytest
from PIL import Image

from conftest import SAMPLE_DIR, make_image_bytes
from subsystem_1_dataset_preprocessing import (CorruptImageError, DatasetError, DatasetErrorHandler,
                                               DatasetManager, DatasetSplit, DatasetStatistics,
                                               EmptyImageError, ImageTooLargeError, ImageTooSmallError,
                                               ImageValidator, PreprocessingPipeline, ResizeStep,
                                               RGBStep, UnsupportedImageError)


def test_valid_png_becomes_rgb():
    assert ImageValidator().validate_and_prepare(make_image_bytes("PNG")).mode == "RGB"


def test_empty_upload_rejected():
    with pytest.raises(EmptyImageError):
        ImageValidator().validate_and_prepare(b"")


def test_corrupt_bytes_rejected():
    with pytest.raises(CorruptImageError):
        ImageValidator().validate_and_prepare(b"this is not an image")


def test_unsupported_format_rejected():
    with pytest.raises(UnsupportedImageError):
        ImageValidator().validate_and_prepare(make_image_bytes("GIF"))


def test_oversized_and_tiny_images_rejected():
    with pytest.raises(ImageTooLargeError):
        ImageValidator(max_bytes=10).validate_and_prepare(make_image_bytes())
    with pytest.raises(ImageTooSmallError):
        ImageValidator().validate_and_prepare(make_image_bytes(size=(20, 20)))


def test_validator_setters_validate():
    validator = ImageValidator()
    with pytest.raises(ValueError):
        validator.max_bytes = 0


def test_pipe_operator_builds_pipeline_and_resizes():
    pipeline = RGBStep() | ResizeStep(50)
    assert len(pipeline) == 2
    result = pipeline.apply(Image.new("L", (200, 100)))
    assert result.mode == "RGB" and max(result.size) == 50


def test_normalized_array_is_between_0_and_1():
    array = PreprocessingPipeline.to_normalized_array(Image.new("RGB", (4, 4), "white"))
    assert array.max() <= 1.0 and array.shape == (4, 4, 3)


def test_split_is_reproducible_and_leak_free():
    manager = DatasetManager(SAMPLE_DIR)
    manager.load_dataset()
    first = manager.split_dataset()
    assert sum(first.values()) == 18 and not manager.dataset_split.has_leakage()
    second = DatasetSplit(seed=42).split(manager.records)
    assert first == second


def test_statistics_report_class_counts():
    stats = DatasetStatistics.from_folder(SAMPLE_DIR)
    assert stats.total_images == 18 and stats.class_counts["Plastic"] == 8
    assert stats.imbalance_ratio == 8.0


def test_manifest_is_written(tmp_path):
    manager = DatasetManager(SAMPLE_DIR)
    manager.load_dataset(); manager.validate_dataset(); manager.split_dataset()
    path = manager.export_manifest(tmp_path / "m.csv")
    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 19 and "checksum" in lines[0]


def test_missing_dataset_folder_raises(tmp_path):
    with pytest.raises(DatasetError):
        DatasetManager(tmp_path / "nope").load_dataset()


def test_error_handler_hides_details():
    response = DatasetErrorHandler().handle(EmptyImageError("internal path C:\\secret"))
    assert response.http_status == 400 and "secret" not in response.message
