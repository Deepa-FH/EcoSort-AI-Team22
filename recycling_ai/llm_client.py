from __future__ import annotations

import base64
import mimetypes
import os
from pathlib import Path

from openai import OpenAI

from .exceptions import LLMServiceError, MissingAPIKeyError


class OpenAICompatibleClient:
    """KIconnect/OpenAI-compatible multimodal chat client."""

    def __init__(self, api_key: str | None, model: str, base_url: str, timeout: int = 60):
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    @staticmethod
    def _image_content(image_path: Path) -> dict:
        mime_type = mimetypes.guess_type(image_path.name)[0] or "image/jpeg"
        encoded = base64.b64encode(image_path.read_bytes()).decode("utf-8")
        return {
            "type": "image_url",
            "image_url": {"url": f"data:{mime_type};base64,{encoded}"},
        }

    def ask(self, prompt: str, image_path: Path | None = None) -> str:
        if not self.api_key:
            raise MissingAPIKeyError("No LLM API key was supplied. Use --api-key or LLM_API_KEY.")

        content: list[dict] = [{"type": "text", "text": prompt}]
        if image_path is not None and image_path.is_file():
            content.append(self._image_content(image_path))

        try:
            client = OpenAI(api_key=self.api_key, base_url=self.base_url, timeout=self.timeout)
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": content}],
            )
            answer = response.choices[0].message.content
            if not answer:
                raise LLMServiceError("The AI service returned an empty answer.")
            return str(answer).strip()
        except LLMServiceError:
            raise
        except Exception as exc:
            raise LLMServiceError(f"The AI service could not answer: {exc}") from exc
