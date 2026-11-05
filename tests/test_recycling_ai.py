import pytest

from ecosort_testing.recycling_ai_errors import LLMServiceError, MissingAPIKeyError, RecyclingAIErrorHandler
from ecosort_testing.sample_services import RecyclingAssistantService


class BrokenLLM:
    def ask(self, material):
        raise ConnectionError("network unavailable")


def test_09_missing_api_key_raises_specific_error():
    with pytest.raises(MissingAPIKeyError):
        RecyclingAssistantService(None, BrokenLLM()).ask_llm("paper")


def test_10_network_failure_is_chained_as_llm_service_error():
    with pytest.raises(LLMServiceError) as captured:
        RecyclingAssistantService("key", BrokenLLM()).ask_llm("paper")
    assert isinstance(captured.value.__cause__, ConnectionError)
    assert RecyclingAIErrorHandler().handle(captured.value).code == "LLM_UNAVAILABLE"


def test_11_assistant_uses_local_fallback_when_llm_fails():
    result = RecyclingAssistantService("key", BrokenLLM()).answer("paper")
    assert result == {"source": "local-fallback", "answer": "Use the blue paper bin."}
