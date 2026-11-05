from collections.abc import Callable

class OpenAICompatibleClient:
    """Keeps runtime API configuration outside source; owned by Mayuresh Kumbhar."""
    def __init__(self, model: str = "mistralai-mistral-small-4", base_url: str = "") -> None:
        self._model, self._base_url, self._api_key, self._sender = model, base_url, None, None
    def initialize(self, api_key: str, sender: Callable[[str], str]) -> None:
        if not api_key.strip(): raise ValueError("API key is required at runtime.")
        self._api_key, self._sender = api_key, sender
    def get_model(self) -> str: return self._model
    def set_model(self, value: str) -> None:
        if not value.strip(): raise ValueError("Model cannot be empty.")
        self._model = value
    def get_base_url(self) -> str: return self._base_url
    def set_base_url(self, value: str) -> None: self._base_url = value.rstrip("/")
    def ask(self, prompt: str) -> str:
        if self._sender is None: raise RuntimeError("LLM client is not initialized.")
        return self._sender(prompt)
