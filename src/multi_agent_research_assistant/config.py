from __future__ import annotations

from dataclasses import dataclass, replace
import os
from typing import Any


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _normalize_provider(provider: str) -> str:
    normalized = (provider or "heuristic").strip().lower()
    if normalized in {"heuristic", "ollama"}:
        return normalized
    return "heuristic"


@dataclass(frozen=True, slots=True)
class Settings:
    llm_provider: str = "heuristic"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    max_queries: int = 5
    max_results_per_query: int = 8
    max_documents: int = 10
    min_document_chars: int = 800

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            llm_provider=_normalize_provider(os.getenv("MARA_LLM_PROVIDER", "heuristic")),
            ollama_base_url=os.getenv("MARA_OLLAMA_BASE_URL", "http://localhost:11434"),
            ollama_model=os.getenv("MARA_OLLAMA_MODEL", "llama3.1:8b"),
            max_queries=max(1, _env_int("MARA_MAX_QUERIES", 5)),
            max_results_per_query=max(1, _env_int("MARA_MAX_RESULTS_PER_QUERY", 8)),
            max_documents=max(1, _env_int("MARA_MAX_DOCUMENTS", 10)),
            min_document_chars=max(200, _env_int("MARA_MIN_DOCUMENT_CHARS", 800)),
        )

    def with_overrides(self, **overrides: Any) -> "Settings":
        clean_overrides = {key: value for key, value in overrides.items() if value is not None}
        if "llm_provider" in clean_overrides:
            clean_overrides["llm_provider"] = _normalize_provider(clean_overrides["llm_provider"])
        return replace(self, **clean_overrides)

