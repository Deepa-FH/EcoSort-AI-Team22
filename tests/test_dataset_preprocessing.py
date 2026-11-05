from io import BytesIO

import pytest
from PIL import Image

from ecosort_testing.dataset_errors import CorruptImageError, EmptyImageError, ImageTooLargeError, UnsupportedImageError
from ecosort_testing.sample_services import ImageValidationService


def test_01_valid_png_is_converted_to_rgb(png_bytes):
    image = ImageValidationService().validate(png_bytes)
    assert image.mode == "RGB" and image.size == (12, 12)


def test_02_empty_image_raises_specific_error():
    with pytest.raises(EmptyImageError):
        ImageValidationService().validate(b"")


def test_03_unsupported_and_corrupt_images_raise_specific_errors():
    stream = BytesIO()
    Image.new("RGB", (3, 3)).save(stream, format="GIF")
    with pytest.raises(UnsupportedImageError):
        ImageValidationService().validate(stream.getvalue())
    with pytest.raises(CorruptImageError):
        ImageValidationService().validate(b"not-an-image")


def test_04_oversized_image_raises_specific_error():
    with pytest.raises(ImageTooLargeError):
        ImageValidationService(max_bytes=3).validate(b"1234")
