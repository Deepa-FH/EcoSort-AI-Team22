from io import BytesIO

import pytest
from PIL import Image

from ecosort_testing.flask_app import create_app
from ecosort_testing.sample_services import ImageValidationService, RecyclingAssistantService


class FakeDetector:
    def predict(self, image):
        return {"label": "Paper", "confidence": 0.91, "size": list(image.size)}


class FakeLLM:
    def ask(self, material):
        return f"Recycle {material} using the local rule."


@pytest.fixture()
def png_bytes():
    stream = BytesIO()
    Image.new("RGB", (12, 12), "white").save(stream, format="PNG")
    return stream.getvalue()


@pytest.fixture()
def app():
    application = create_app(ImageValidationService(), FakeDetector(), RecyclingAssistantService("test-key", FakeLLM()))
    application.config.update(TESTING=True)
    return application


@pytest.fixture()
def client(app):
    return app.test_client()
