from io import BytesIO
from PIL import Image
from dataset_preprocessing.image_validator import ImageValidator
from dataset_preprocessing.exceptions import ImageTooLargeError, PreprocessingError
from image_recognition.confidence_filter import ConfidenceFilter
from image_recognition.detection_models import BoundingBox, Detection
from recycling_ai.ai_assistant import WasteAssistant
from recycling_ai.fallback_responses import fallback_response
from recycling_ai.llm_client import OpenAICompatibleClient
from recycling_ai.recycling_rules import RecyclingRuleEngine


def image_bytes(fmt="PNG", size=(10, 10)):
    stream = BytesIO(); Image.new("RGB", size, "white").save(stream, format=fmt); return stream.getvalue()


def test_valid_image(): assert ImageValidator().validate_and_prepare(image_bytes()).mode == "RGB"
def test_empty_image():
    try: ImageValidator().validate_and_prepare(b""); assert False
    except PreprocessingError: assert True
def test_invalid_image():
    try: ImageValidator().validate_and_prepare(b"bad"); assert False
    except PreprocessingError: assert True
def test_large_image_bytes():
    try: ImageValidator(max_bytes=2).validate_and_prepare(b"123"); assert False
    except ImageTooLargeError: assert True
def test_detection_percentage(): assert Detection("paper", .75, BoundingBox(0,0,1,1)).confidence_percent == 75.0
def test_box_list(): assert BoundingBox(0,1,2,3).as_list() == [0,1,2,3]
def test_confidence_filter(): assert len(list(ConfidenceFilter(.5).filter([Detection("a",.4,BoundingBox(0,0,1,1)),Detection("b",.6,BoundingBox(0,0,1,1))]))) == 1
def test_iterator():
    from image_recognition.detector import DetectionStream
    assert len(list(DetectionStream([Detection("a",.8,BoundingBox(0,0,1,1))]))) == 1
def test_rules(): assert RecyclingRuleEngine.default_rules().get("paper").bin_name == "Paper recycling"
def test_unknown_rule(): assert RecyclingRuleEngine.default_rules().get("unknown") is None
def test_fallback(): assert "Glass" in fallback_response(RecyclingRuleEngine.default_rules().get("glass"))
def test_missing_api_key():
    try: OpenAICompatibleClient(None,"x","http://localhost").ask("hi"); assert False
    except Exception as error: assert "API key" in str(error)
def test_assistant_fallback():
    result=WasteAssistant(RecyclingRuleEngine.default_rules(),OpenAICompatibleClient(None,"x","http://localhost")).answer("paper","what now?")
    assert result["source"] == "local-fallback"
def test_prompt_source():
    class Fake:
        def ask(self,prompt): return "Keep it dry."
    assert WasteAssistant(RecyclingRuleEngine.default_rules(),Fake()).answer("paper","help")["source"] == "llm"
def test_pipeline_operator():
    from dataset_preprocessing.preprocessing_pipeline import RGBStep, ResizeStep
    assert (RGBStep() | ResizeStep()).apply(Image.new("L",(100,100))).mode == "RGB"
