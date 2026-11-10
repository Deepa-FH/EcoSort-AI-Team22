"""End-to-end test with the REAL trained YOLO model (skipped if ultralytics is missing)."""

import pytest

from conftest import ROOT, SAMPLE_DIR, login

pytest.importorskip("ultralytics", reason="ultralytics not installed")


@pytest.fixture(scope="module")
def real_client(tmp_path_factory):
    from subsystem_4_web_integration import AppConfig, create_application
    from subsystem_3_recycling_ai import OpenAICompatibleClient
    config = AppConfig(root=ROOT, data_dir=tmp_path_factory.mktemp("data"), model_path=ROOT / "models" / "best_model.pt",
                       api_key=None, tunnel_enabled=False, open_browser=False)
    app = create_application(config, llm_client=OpenAICompatibleClient(None, "m", "http://x"),
                             run_reviews_in_background=False)
    app.warm_up()
    c = app.flask_app.test_client()
    login(c)
    return c


@pytest.mark.parametrize("filename,expected", [
    ("realwaste__Plastic__Plastic_801.jpg", "Plastic"),
    ("realwaste__Metal__Metal_42.jpg", "Metal"),
    ("trashpanda__Biomuell__Biomuell_0092.jpg", "Biomuell"),
])
def test_real_model_classifies_sample_photos(real_client, filename, expected):
    with open(SAMPLE_DIR / filename, "rb") as handle:
        body = real_client.post("/api/analyze", data={"photo": (handle, filename), "threshold": "50"},
                                content_type="multipart/form-data").get_json()
    assert body["top"]["label"] == expected and body["route"]["bin"]
