"""Shared test fixtures.

Fakes replace the two slow / external parts so the tests run in seconds,
offline and without an API key:
    FakeDetector  - stands in for the YOLO model (Subsystem 2)
    FakeLLM       - stands in for the web API (Subsystem 3)
The real model is exercised in ``test_integration.py``.
"""

import sys
from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))      # lets tests import the subsystem packages

from subsystem_2_image_recognition import BoundingBox, Detection  # noqa: E402
from subsystem_3_recycling_ai import LLMServiceError, MissingAPIKeyError  # noqa: E402
from subsystem_4_web_integration import AppConfig, create_application  # noqa: E402

SAMPLE_DIR = ROOT / "sample_data"


def make_image_bytes(fmt="PNG", size=(120, 120), color="white") -> bytes:
    """Create a small in-memory image file."""
    stream = BytesIO()
    Image.new("RGB", size, color).save(stream, format=fmt)
    return stream.getvalue()


class FakeDetector:
    """Returns a fixed detection list. ``confidence`` controls the review path."""

    labels = ["Biomuell", "Glass", "Metal", "Papier", "Plastic", "Sondermuell", "Textile_Trash"]
    model_version = "fake-model"

    def __init__(self, label="Plastic", confidence=0.9, fail=False):
        self.label, self.confidence, self.fail = label, confidence, fail

    def load(self):
        pass

    def predict(self, image):
        if self.fail:
            raise RuntimeError("boom")
        return [Detection(self.label, self.confidence, BoundingBox(1, 2, 50, 60))]


class FakeLLM:
    """Stands in for ``OpenAICompatibleClient``."""

    def __init__(self, answer="Object: Bottle\nBin: Blue paper bin", configured=True, error=None):
        self.answer, self.error = answer, error
        self._configured = configured
        self.prompts = []

    @property
    def is_configured(self):
        return self._configured

    def ask(self, prompt, image_path=None):
        self.prompts.append(prompt)
        if not self._configured:
            raise MissingAPIKeyError("no key")
        if self.error:
            raise LLMServiceError(self.error)
        return self.answer


@pytest.fixture
def config(tmp_path):
    return AppConfig(root=ROOT, data_dir=tmp_path, model_path=ROOT / "models" / "best_model.pt",
                     api_key=None, tunnel_enabled=False, open_browser=False)


@pytest.fixture
def build_client(config):
    """Factory: ``build_client(detector=..., llm=...)`` -> logged-out Flask test client."""
    def _build(detector=None, llm=None):
        app = create_application(config, detector=detector or FakeDetector(),
                                 llm_client=llm or FakeLLM(), run_reviews_in_background=False)
        return app.flask_app.test_client()
    return _build


def login(client, username="admin", password="admin", role=None):
    """Sign in through the real login form. ``role`` = the "Sign in as" choice."""
    data = {"username": username, "password": password}
    if role:
        data["role"] = role
    return client.post("/login", data=data)


def register(client, username, role, password="secret1"):
    """Create an account through the sign-up form (invitation code ``pythonai``)."""
    return client.post("/signup", data={"username": username, "password": password,
                                        "role": role, "signup_code": "pythonai"})


@pytest.fixture
def client(build_client):
    """Logged-in admin client with a confident fake detector."""
    c = build_client()
    login(c)
    return c
