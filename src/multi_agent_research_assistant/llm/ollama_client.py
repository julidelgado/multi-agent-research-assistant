from __future__ import annotations

from typing import Any

try:
    from ollama import Client
except ImportError:  # pragma: no cover
    Client = None  # type: ignore[assignment]


class OllamaLLMClient:
    name = "ollama"

    def __init__(self, model: str, base_url: str, temperature: float = 0.2):
        if Client is None:
            raise RuntimeError("Ollama package is not installed.")
        self.model = model
        self.temperature = temperature
        self._client = Client(host=base_url)

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        messages: list[dict[str, Any]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        try:
            response = self._client.chat(
                model=self.model,
                messages=messages,
                options={"temperature": self.temperature},
            )
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"Ollama request failed: {exc}") from exc
        return (response.get("message", {}).get("content", "") or "").strip()

