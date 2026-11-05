import pytest
from app import parse_image, check_confidence, ask_service, validate_material
from exceptions import DatasetError, RecognitionError, RecyclingAIError, DashboardError

def test_image_required():
    with pytest.raises(DatasetError): parse_image("")
def test_image_extension():
    with pytest.raises(DatasetError): parse_image("file.txt")
def test_jpg_accepted(): assert parse_image("file.jpg")
def test_png_accepted(): assert parse_image("file.png")
def test_webp_accepted(): assert parse_image("file.webp")
def test_confidence_low():
    with pytest.raises(RecognitionError): check_confidence(0)
def test_confidence_high():
    with pytest.raises(RecognitionError): check_confidence(1.1)
def test_confidence_ok(): assert check_confidence(.8)==.8
def test_api_key_missing():
    with pytest.raises(RecyclingAIError): ask_service(None)
def test_api_key_ok(): assert ask_service("key")=="answer"
def test_material_missing():
    with pytest.raises(DashboardError): validate_material("")
def test_material_ok(): assert validate_material(" paper ")=="paper"
def test_material_none():
    with pytest.raises(DashboardError): validate_material(None)
def test_bad_image_case():
    with pytest.raises(DatasetError): parse_image("file.gif")
def test_confidence_boundary(): assert check_confidence(1)==1
