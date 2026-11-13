"""Subsystem 3 - exceptions and error handler (owner: Mayuresh Kumbhar).

    EcoSortError
      +-- RecyclingAIError
            +-- LLMServiceError        (API unreachable / empty answer)
            |     +-- MissingAPIKeyError
            +-- UnknownMaterialError   (no rule for this waste label)
            +-- InvalidRuleError       (an admin edit is incomplete)
"""

from shared.error_handling import BaseErrorHandler, EcoSortError


class RecyclingAIError(EcoSortError):
    """Base class for rules and Ask-AI problems."""

    code = "RECYCLING_AI_ERROR"
    safe_message = "The recycling guidance is not available right now."
    http_status = 500


class LLMServiceError(RecyclingAIError):
    """The AI service could not answer (network, quota, empty answer ...)."""

    code = "LLM_UNAVAILABLE"
    safe_message = "Sortly AI is not reachable right now. Local recycling rules are still available."
    http_status = 502
    recoverable = True


class MissingAPIKeyError(LLMServiceError):
    """No API key was supplied (``--api-key`` or ``LLM_API_KEY``)."""

    code = "MISSING_API_KEY"
    safe_message = ("Ask AI needs an API key. Start the app with --api-key YOUR_KEY "
                    "or set the LLM_API_KEY environment variable.")
    http_status = 503


class UnknownMaterialError(RecyclingAIError):
    """There is no recycling rule for the requested label."""

    code = "UNKNOWN_MATERIAL"
    safe_message = "Unknown waste label."
    http_status = 404
    recoverable = True


class InvalidRuleError(RecyclingAIError):
    """A rule edit is missing required fields."""

    code = "INVALID_RULE"
    safe_message = "All rule fields are required."
    http_status = 400
    recoverable = True


class RecyclingAIErrorHandler(BaseErrorHandler):
    """Error handler of Subsystem 3 (logic inherited from ``BaseErrorHandler``)."""

    subsystem = "recycling_ai"
