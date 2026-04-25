from __future__ import annotations

from app.rag.llm.base import BaseLLMClient


class OpenAIClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("openai package is not installed") from exc

        client = OpenAI(api_key=self.api_key)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        completion = client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        return completion.choices[0].message.content or ""
