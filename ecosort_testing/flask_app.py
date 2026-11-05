"""Minimal Flask boundary matching the Sortly upload workflow."""
from flask import Flask, jsonify, request

from .dataset_errors import DatasetError, DatasetErrorHandler
from .web_errors import MissingUploadError, WebDashboardErrorHandler


def create_app(validator, detector, assistant) -> Flask:
    app = Flask(__name__)
    dataset_handler = DatasetErrorHandler()
    web_handler = WebDashboardErrorHandler()

    @app.get("/health")
    def health():
        return jsonify(status="ok", application="Sortly AI test application")

    @app.post("/predict")
    def predict():
        upload = request.files.get("photo")
        if upload is None or not upload.filename:
            result = web_handler.handle(MissingUploadError())
            return jsonify(result.as_dict()), result.http_status
        try:
            image = validator.validate(upload.read())
            return jsonify(detector.predict(image))
        except DatasetError as exc:
            result = dataset_handler.handle(exc)
            return jsonify(result.as_dict()), result.http_status
        except Exception:
            app.logger.exception("Unexpected detector failure")
            result = web_handler.handle(RuntimeError("internal detail"))
            return jsonify(result.as_dict()), result.http_status

    @app.post("/ask-ai")
    def ask_ai():
        payload = request.get_json(silent=True) or {}
        material = str(payload.get("material", "")).strip()
        if not material:
            return jsonify(error="material is required"), 400
        return jsonify(assistant.answer(material))

    return app
