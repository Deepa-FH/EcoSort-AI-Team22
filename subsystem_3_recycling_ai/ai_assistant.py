"""WasteAssistant - rules first, LLM for wording, local fallback when the LLM fails.

OOP idea: COMPOSITION + DEPENDENCY INJECTION. The assistant receives its three
helpers in the constructor; tests pass fakes, production passes the real ones.
"""

from __future__ import annotations

from pathlib import Path

from .exceptions import LLMServiceError
from .fallback_responses import FallbackResponder
from .guidance_response import SOURCE_LLM, SOURCE_LOCAL, GuidanceResponse
from .llm_client import OpenAICompatibleClient
from .prompt_builder import PromptBuilder
from .recycling_rules import RecyclingRuleEngine


class WasteAssistant:
    """High-level API of Subsystem 3 used by the web integration layer."""

    def __init__(self, rules: RecyclingRuleEngine, llm: OpenAICompatibleClient,
                 prompt_builder: PromptBuilder | None = None,
                 fallback: FallbackResponder | None = None):
        self._rules = rules
        self._llm = llm
        self._prompts = prompt_builder or PromptBuilder()
        self._fallback = fallback or FallbackResponder()

    # ---- accessors -------------------------------------------------------
    @property
    def rules(self) -> RecyclingRuleEngine:
        return self._rules

    @property
    def llm(self) -> OpenAICompatibleClient:
        return self._llm

    @property
    def ai_available(self) -> bool:
        """True when an API key is configured."""
        return self._llm.is_configured

    # ---- helpers ---------------------------------------------------------
    @staticmethod
    def _estimate_tokens(prompt: str, answer: str) -> int:
        """Rough token count (about 4 characters per token)."""
        return max(1, (len(prompt) + len(answer)) // 4)

    def _local_guidance(self, label: str | None, notice: str) -> GuidanceResponse:
        rule = self._rules.get(label)
        return GuidanceResponse(self._fallback.respond(rule), SOURCE_LOCAL, label if rule else None,
                                rule.bin if rule else "", 0, notice)

    # ---- use cases -------------------------------------------------------
    def review_detection(self, detections: list[dict], image_path: Path | None = None) -> GuidanceResponse:
        """Second opinion for a photo the model is unsure about.

        Tries the LLM; if that fails (no key, no internet ...) the best local
        rule is returned instead and ``notice`` explains why.
        """
        prompt = self._prompts.build_review_prompt(detections, self._rules.rules_as_text())
        top_label = detections[0]["label"] if detections else None
        try:
            answer = self._llm.ask(prompt, image_path)
        except LLMServiceError as error:
            return self._local_guidance(top_label, error.safe_message)
        label = self._rules.find_label_in_text(answer)
        rule = self._rules.get(label)
        return GuidanceResponse(answer, SOURCE_LLM, label, rule.bin if rule else "",
                                self._estimate_tokens(prompt, answer))

    def chat(self, message: str, prediction: str = "No current model prediction",
             image_path: Path | None = None) -> GuidanceResponse:
        """Answer a free-text question. Raises ``LLMServiceError`` on failure
        (the web layer converts it into a friendly message)."""
        prompt = self._prompts.build_chat_prompt(message, prediction)
        answer = self._llm.ask(prompt, image_path)
        return GuidanceResponse(answer, SOURCE_LLM, None, "", self._estimate_tokens(prompt, answer))
