"""IntegrationController - connects the four subsystems into use cases.

The Flask routes call ONLY this class. It owns no web code (no ``request``)
and no SQL, so each use case can be tested without a browser.
"""

from __future__ import annotations

from pathlib import Path

from subsystem_3_recycling_ai import RecyclingRuleEngine, WasteAssistant

from .dashboard_service import DashboardService
from .exceptions import MissingUploadError, ValidationFailedError
from .review_jobs import ReviewJobManager
from .scan_service import ScanService, is_valid_photo_name
from .waste_repository import WasteRepository

MAX_QUESTION_LENGTH = 1200


class IntegrationController:
    """Use cases of the application: scan, chat, review status, rules."""

    def __init__(self, scan_service: ScanService, assistant: WasteAssistant, rules: RecyclingRuleEngine,
                 jobs: ReviewJobManager, dashboard: DashboardService, repository: WasteRepository,
                 default_threshold_percent: float = 50):
        self._scans = scan_service
        self._assistant = assistant
        self._rules = rules
        self._jobs = jobs
        self._dashboard = dashboard
        self._repository = repository
        self._default_threshold_percent = default_threshold_percent

    # ---- read-only accessors used by the web layer ------------------------
    @property
    def dashboard(self) -> DashboardService:
        return self._dashboard

    @property
    def repository(self) -> WasteRepository:
        return self._repository

    @property
    def rules(self) -> RecyclingRuleEngine:
        return self._rules

    @property
    def ai_available(self) -> bool:
        return self._assistant.ai_available

    @property
    def capture_dir(self) -> Path:
        return self._scans.capture_dir

    # ---- use cases -------------------------------------------------------
    def warm_up(self) -> None:
        """Load the model at start-up."""
        self._scans.warm_up()

    def analyze_photo(self, image_bytes: bytes | None, threshold_percent, user_id: int | None) -> dict:
        """Scan one photo. Returns the JSON dict for ``/api/analyze``.

        If the model is unsure, a background review job is started and its id
        is added as ``job_id``.
        """
        if not image_bytes:
            raise MissingUploadError("no 'photo' field or empty file")
        try:
            percent = float(threshold_percent)
        except (TypeError, ValueError):
            percent = self._default_threshold_percent
        outcome = self._scans.analyze(image_bytes, percent, user_id)
        response = outcome.response
        if outcome.prediction.needs_review:
            detections = [d.to_dict() for d in outcome.prediction.detections]
            response["job_id"] = self._jobs.start(outcome.scan_id, user_id, outcome.image_path, detections)
        return response

    def chat(self, payload: dict, user_id: int | None) -> dict:
        """Answer a chat question with Subsystem 3. Returns the JSON for ``/api/chat``."""
        message = str(payload.get("message", "")).strip()
        if not message:
            raise ValidationFailedError("Please enter a question.")
        if len(message) > MAX_QUESTION_LENGTH:
            raise ValidationFailedError("Please keep the question under 1,200 characters.")
        image_path = None
        image_name = str(payload.get("image_name", ""))
        if is_valid_photo_name(image_name):
            candidate = self._scans.capture_dir / image_name
            if candidate.exists():
                image_path = candidate
        prediction = str(payload.get("prediction", "No current model prediction"))[:300]
        guidance = self._assistant.chat(message, prediction, image_path)
        self._repository.add_usage(user_id, "chat", guidance.estimated_tokens)
        return {"answer": guidance.answer, "estimated_tokens": guidance.estimated_tokens, "source": guidance.source}

    def review_status(self, job_id: str) -> dict:
        return self._jobs.get(job_id)

    def update_rule(self, payload: dict) -> dict:
        """Admin edit of one rule. Returns all rules afterwards."""
        label = str(payload.get("label", ""))
        self._rules.update(label, {key: payload.get(key, "") for key in ("category", "bin", "bin_de", "color",
                                                                        "hex", "theme", "symbol", "note")})
        return self._rules.as_dicts()
