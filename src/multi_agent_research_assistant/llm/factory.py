from __future__ import annotations

from multi_agent_research_assistant.config import Settings

from .heuristic import HeuristicLLMClient
from .ollama_client import OllamaLLMClient


def build_llm_client(settings: Settings):
    if settings.llm_provider == "ollama":
        try:
            return OllamaLLMClient(
                model=settings.ollama_model,
                base_url=settings.ollama_base_url,
            )
        except Exception:
            return HeuristicLLMClient()
    return HeuristicLLMClient()

