"""OpenAICompatibleClient - talks to any OpenAI-style chat API (e.g. KIconnect NRW).

The API key never lives in source code: it comes from ``--api-key`` or the
``LLM_API_KEY`` environment variable (PPT: "Protect API keys").
"""

from __future__ import annotations

import base64
import mimetypes
import os
from pathlib import Path

from .exceptions import LLMServiceError, MissingAPIKeyError


class OpenAICompatibleClient:
    """Sends a prompt (and optionally a photo) to the LLM and returns the answer."""

    def __init__(self, api_key: str | None, model: str, base_url: str, timeout: int = 60):
        self._api_key = api_key or os.getenv("LLM_API_KEY") or None
        self.model = model
        self.base_url = base_url
        self.timeout = timeout

    # ---- properties ------------------------------------------------------
    @property
    def api_key(self) -> str | None:
        return self._api_key

    @api_key.setter
    def api_key(self, value: str | None) -> None:
        self._api_key = (value or "").strip() or None

    @property
    def base_url(self) -> str:
        return self._base_url

    @base_url.setter
    def base_url(self, value: str) -> None:
        self._base_url = str(value).rstrip("/")     # "https://x/v1/" -> "https://x/v1"

    @property
    def is_configured(self) -> bool:
        """True when a key is available (the UI shows 'AI ready' from this)."""
        return self._api_key is not None

    def __repr__(self) -> str:
        # NEVER print the key. Only show whether one exists.
        return (f"OpenAICompatibleClient(model={self.model!r}, base_url={self._base_url!r}, "
                f"api_key={'set' if self.is_configured else 'missing'})")

    # ---- behaviour -------------------------------------------------------
    @staticmethod
    def _image_content(image_path: Path) -> dict:
        """Encode a photo as a base64 'data URL' the API understands."""
        mime = mimetypes.guess_type(image_path.name)[0] or "image/jpeg"
        encoded = base64.b64encode(image_path.read_bytes()).decode("utf-8")
        return {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{encoded}"}}

    def ask(self, prompt: str, image_path: Path | None = None) -> str:
        """Ask the LLM. Raises ``MissingAPIKeyError`` or ``LLMServiceError``.

        DEBUG: ``LLMServiceError.detail`` (in the server log) contains the
        original network/API error text. Typical causes: wrong key (401),
        wrong ``--llm-base-url``, no internet, model name not available.
        """
        if not self._api_key:
            raise MissingAPIKeyError("No LLM API key was supplied. Use --api-key or LLM_API_KEY.")

        content: list[dict] = [{"type": "text", "text": prompt}]
        if image_path is not None and Path(image_path).is_file():
            content.append(self._image_content(Path(image_path)))
        try:
            from openai import OpenAI              # imported here: not needed without an API key
            client = OpenAI(api_key=self._api_key, base_url=self._base_url, timeout=self.timeout)
            response = client.chat.completions.create(
                model=self.model, messages=[{"role": "user", "content": content}])
            answer = response.choices[0].message.content
            if not answer:
                raise LLMServiceError("The AI service returned an empty answer.")
            return str(answer).strip()
        except LLMServiceError:
            raise
        except Exception as error:
            raise LLMServiceError(f"The AI service could not answer: {error}") from error
