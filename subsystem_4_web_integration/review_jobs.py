"""ReviewJobManager - runs the slow LLM review in the background.

The browser gets the local YOLO answer immediately, then polls
``/api/review/<job_id>`` until the AI has finished.
"""

from __future__ import annotations

import threading
import uuid
from pathlib import Path

from subsystem_3_recycling_ai import WasteAssistant

from .exceptions import JobNotFoundError
from .waste_repository import WasteRepository

MAX_REMEMBERED_JOBS = 200       # old finished jobs are dropped so memory cannot grow forever


class ReviewJobManager:
    """Starts review jobs (in a thread) and remembers their status."""

    def __init__(self, assistant: WasteAssistant, repository: WasteRepository, run_in_background: bool = True):
        self._assistant = assistant
        self._repository = repository
        self._run_in_background = run_in_background     # tests set False => runs immediately
        self._jobs: dict[str, dict] = {}
        self._lock = threading.Lock()                   # several threads touch _jobs

    def start(self, scan_id: int, user_id: int | None, image_path: Path, detections: list[dict]) -> str:
        """Create a job and return its id."""
        job_id = uuid.uuid4().hex
        self._set(job_id, {"status": "working"})
        if self._run_in_background:
            threading.Thread(target=self._run, args=(job_id, scan_id, user_id, image_path, detections),
                             daemon=True).start()
        else:
            self._run(job_id, scan_id, user_id, image_path, detections)
        return job_id

    def get(self, job_id: str) -> dict:
        """Current status of a job. Raises ``JobNotFoundError`` for unknown ids."""
        with self._lock:
            job = self._jobs.get(job_id)
        if job is None:
            raise JobNotFoundError(f"unknown job {job_id}")
        return dict(job)

    # ---- internals -------------------------------------------------------
    def _set(self, job_id: str, value: dict) -> None:
        with self._lock:
            self._jobs[job_id] = value
            while len(self._jobs) > MAX_REMEMBERED_JOBS:      # dicts keep insertion order
                self._jobs.pop(next(iter(self._jobs)))

    def _run(self, job_id: str, scan_id: int, user_id: int | None, image_path: Path,
             detections: list[dict]) -> None:
        """Worker: ask Subsystem 3, store the result, publish the job status."""
        try:
            guidance = self._assistant.review_detection(detections, image_path)
            self._repository.update_scan_review(scan_id, guidance.source, guidance.estimated_tokens,
                                                guidance.label, llm_used=guidance.used_llm)
            if guidance.used_llm:
                self._repository.add_usage(user_id, "review", guidance.estimated_tokens)
            self._set(job_id, {"status": "done", "answer": guidance.answer, "source": guidance.source,
                               "label": guidance.label, "notice": guidance.notice})
        except Exception as error:            # a background thread must never crash silently
            import logging
            logging.getLogger("ecosort").exception("Review job failed", exc_info=error)
            self._set(job_id, {"status": "error", "message": "The review could not be completed."})
