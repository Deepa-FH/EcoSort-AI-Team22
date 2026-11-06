from io import BytesIO


def test_12_health_endpoint_returns_json(client):
    response = client.get("/health")
    assert response.status_code == 200 and response.json["status"] == "ok"


def test_13_predict_without_upload_returns_400(client):
    response = client.post("/predict", data={})
    assert response.status_code == 400 and response.json["code"] == "UPLOAD_REQUIRED"


def test_14_preprocessing_exception_returns_safe_400(client):
    response = client.post("/predict", data={"photo": (BytesIO(b"bad"), "bad.png")}, content_type="multipart/form-data")
    assert response.status_code == 400
    assert response.json["code"] == "DATASET_CORRUPT"
    assert "Traceback" not in response.get_data(as_text=True)


def test_15_unexpected_detector_failure_returns_safe_500(app, png_bytes):
    class BrokenDetector:
        def predict(self, image):
            raise RuntimeError("secret model path")
    from ecosort_testing.flask_app import create_app
    from ecosort_testing.sample_services import ImageValidationService, RecyclingAssistantService
    class NoopLLM:
        def ask(self, material): return "ok"
    broken_app = create_app(ImageValidationService(), BrokenDetector(), RecyclingAssistantService("key", NoopLLM()))
    broken_app.config.update(TESTING=True)
    response = broken_app.test_client().post("/predict", data={"photo": (BytesIO(png_bytes), "valid.png")}, content_type="multipart/form-data")
    assert response.status_code == 500 and response.json["code"] == "WEB_UNKNOWN"
    assert "secret model path" not in response.get_data(as_text=True)
