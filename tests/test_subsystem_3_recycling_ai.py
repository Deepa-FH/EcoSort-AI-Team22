"""Tests for Subsystem 3 - Recycling Rules & Ask AI (Mayuresh)."""

import pytest

from conftest import FakeLLM
from subsystem_3_recycling_ai import (InMemoryRuleStore, InvalidRuleError, LLMServiceError, MissingAPIKeyError,
                                      OpenAICompatibleClient, PromptBuilder, RecyclingAIErrorHandler,
                                      RecyclingRuleEngine, UnknownMaterialError, WasteAssistant)


@pytest.fixture
def engine():
    return RecyclingRuleEngine(InMemoryRuleStore())


def test_rule_lookup(engine):
    assert engine.get("Papier").bin == "Blue paper bin"
    assert engine.get("Banana") is None and engine.get(None) is None


def test_unknown_label_raises_on_require(engine):
    with pytest.raises(UnknownMaterialError):
        engine.require("Banana")


def test_admin_update_changes_rule(engine):
    fields = engine.get("Glass").to_dict()
    fields["note"] = "New guidance"
    engine.update("Glass", fields)
    assert engine.get("Glass").note == "New guidance"


def test_incomplete_update_rejected(engine):
    fields = engine.get("Glass").to_dict()
    fields["bin"] = "  "
    with pytest.raises(InvalidRuleError):
        engine.update("Glass", fields)


def test_find_label_in_llm_text(engine):
    assert engine.find_label_in_text("Put it in the Blue paper bin please") == "Papier"


def test_prompt_contains_predictions_and_rules(engine):
    prompt = PromptBuilder().build_review_prompt([{"label": "Glass", "confidence": 0.42}], engine.rules_as_text())
    assert "Glass (42%)" in prompt and "Papiertonne" in prompt


def test_client_without_key_raises_and_hides_key():
    client = OpenAICompatibleClient(None, "m", "http://x/")
    assert client.base_url == "http://x" and not client.is_configured
    with pytest.raises(MissingAPIKeyError):
        client.ask("hi")
    client.api_key = "super-secret"
    assert "super-secret" not in repr(client)


def test_assistant_uses_llm_when_available(engine):
    result = WasteAssistant(engine, FakeLLM()).review_detection([{"label": "Glass", "confidence": 0.3}])
    assert result.used_llm and result.label == "Papier" and result.estimated_tokens > 0


def test_assistant_falls_back_to_local_rules(engine):
    result = WasteAssistant(engine, FakeLLM(configured=False)).review_detection([{"label": "Glass", "confidence": 0.3}])
    assert result.source == "local-fallback" and "Pfand" in result.answer and result.notice


def test_chat_propagates_llm_errors(engine):
    with pytest.raises(LLMServiceError):
        WasteAssistant(engine, FakeLLM(error="network down")).chat("hello")


def test_error_handler_gives_safe_message():
    response = RecyclingAIErrorHandler().handle(LLMServiceError("401 key=abc123"))
    assert "abc123" not in response.message and response.http_status == 502
