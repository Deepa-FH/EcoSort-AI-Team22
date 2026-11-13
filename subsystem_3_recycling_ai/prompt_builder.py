"""PromptBuilder - creates the texts sent to the LLM.

Keeping prompts in one class means they can be tuned (and tested) without
touching any network code.
"""

from __future__ import annotations


class PromptBuilder:
    """Builds the two kinds of prompts used by the app."""

    def build_review_prompt(self, detections: list[dict], rules_text: str) -> str:
        """Prompt for the 'second opinion' on a low-confidence photo.

        Args:
            detections: list of ``{"label", "confidence", ...}`` dicts from Subsystem 2.
            rules_text: the administrator-maintained rules (ground truth).
        """
        summary = ", ".join(f"{d['label']} ({d['confidence']:.0%})" for d in detections) or "No object detected"
        return (
            "Answer entirely in English. You are helping sort one waste item in Germany. "
            f"The local model predictions are: {summary}. Treat these as hints, not facts. "
            "Identify the visible object and recommend the correct German disposal route, "
            "including a deposit return if applicable. Do not guess if the photo is unclear. "
            "Use exactly these five English lines:\n"
            "Object: ...\nBin: ...\nReason: ...\nConfidence: high/medium/low\n"
            "Note: ...\n"
            "Mention when local municipal rules or a deposit symbol should be checked. "
            "Use the following administrator-maintained local rules as guidance:\n"
            f"{rules_text}\n"
            "Respond in English only."
        )

    def build_chat_prompt(self, message: str, prediction: str) -> str:
        """Prompt for a free-text question in the chat."""
        return (
            "Answer entirely in English as a friendly German waste-sorting assistant. "
            "Give practical, concise guidance and mention Pfand or local municipal differences when relevant. "
            f"Current custom YOLO context: {prediction}. "
            f"User question: {message}"
        )
