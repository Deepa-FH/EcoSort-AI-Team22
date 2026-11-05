from __future__ import annotations

import os
import json
from urllib import error, request
from .exceptions import LLMServiceError, MissingAPIKeyError


class OpenAICompatibleClient:
    def __init__(self, api_key: str | None, model: str, base_url: str, timeout: int = 30):
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def ask(self, prompt: str) -> str:
        if not self.api_key:
            raise MissingAPIKeyError("No LLM API key was supplied. Use --api-key or LLM_API_KEY.")
        try:
            payload = json.dumps({"model": self.model, "messages": [{"role": "user", "content": prompt}]}).encode("utf-8")
            http_request = request.Request(f"{self.base_url}/chat/completions", data=payload, headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}, method="POST")
            with request.urlopen(http_request, timeout=self.timeout) as response:
                content = json.loads(response.read().decode("utf-8"))["choices"][0]["message"]["content"]
            if not content:
                raise LLMServiceError("The LLM returned an empty answer.")
            return str(content).strip()
        except (error.URLError, error.HTTPError, KeyError, IndexError, TypeError, ValueError, TimeoutError) as error:
            raise LLMServiceError("The LLM service could not answer the request.") from error
