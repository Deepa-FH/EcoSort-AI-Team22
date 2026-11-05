from __future__ import annotations

import base64
from io import BytesIO
from flask import Flask, jsonify, render_template, request
from PIL import Image

from dataset_preprocessing.exceptions import PreprocessingError
from dataset_preprocessing.image_validator import ImageValidator
from recycling_ai.ai_assistant import WasteAssistant


def create_app(detector, validator: ImageValidator, assistant: WasteAssistant) -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/health")
    def health():
        return jsonify(status="ok", labels=detector.labels)

    @app.post("/predict")
    def predict():
        upload = request.files.get("photo")
        if upload is None or not upload.filename:
            return jsonify(error="Choose an image first."), 400
        try:
            image = validator.validate_and_prepare(upload.read())
            result = detector.predict(image)
            annotated = Image.fromarray(result.pop("annotated_array")[..., ::-1])
            buffer = BytesIO()
            annotated.save(buffer, format="JPEG", quality=88)
            result["annotated_image"] = "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")
            return jsonify(result)
        except PreprocessingError as error:
            return jsonify(error=str(error)), 400
        except Exception:
            app.logger.exception("Prediction failed")
            return jsonify(error="Prediction failed."), 500

    @app.post("/ask-ai")
    def ask_ai():
        payload = request.get_json(silent=True) or {}
        material = str(payload.get("material", "")).strip()
        message = str(payload.get("message", "How should I recycle this?"))
        if not material:
            return jsonify(error="material is required"), 400
        return jsonify(assistant.answer(material, message))

    return app
