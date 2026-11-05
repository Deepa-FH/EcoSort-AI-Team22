class RecyclingAIError(Exception):
    """Base error for recycling advice and LLM communication."""


class LLMServiceError(RecyclingAIError):
    pass


class MissingAPIKeyError(LLMServiceError):
    pass
