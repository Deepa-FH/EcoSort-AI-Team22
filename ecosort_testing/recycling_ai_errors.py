"""Mayuresh Kumbhar: Recycling Rules and Ask AI error boundary."""
from .common import ErrorResult


class RecyclingAIError(Exception):
    """Base exception for rules and external language-model assistance."""


class MissingAPIKeyError(RecyclingAIError): pass
class RuleNotFoundError(RecyclingAIError): pass
class LLMServiceError(RecyclingAIError): pass
class EmptyLLMResponseError(RecyclingAIError): pass


class RecyclingAIErrorHandler:
    subsystem = "Recycling Rules and Ask AI"
    _mapping = {
        MissingAPIKeyError: ("MISSING_API_KEY", "AI is unavailable; local recycling rules will be used.", 200),
        RuleNotFoundError: ("RULE_NOT_FOUND", "No verified local rule is available for this material.", 404),
        LLMServiceError: ("LLM_UNAVAILABLE", "AI is unavailable; local recycling rules will be used.", 200),
        EmptyLLMResponseError: ("EMPTY_AI_RESPONSE", "AI returned no advice; local rules will be used.", 200),
    }

    def handle(self, error: Exception) -> ErrorResult:
        code, message, status = self._mapping.get(type(error), ("RECYCLING_AI_UNKNOWN", "Recycling advice is temporarily unavailable.", 500))
        return ErrorResult(self.subsystem, code, message, status, status == 200)
