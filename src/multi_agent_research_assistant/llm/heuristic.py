from __future__ import annotations

import re


class HeuristicLLMClient:
    name = "heuristic"

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        text = prompt.strip()
        if not text:
            return ""
        sentence_chunks = [chunk.strip() for chunk in re.split(r"(?<=[.!?])\s+", text) if chunk.strip()]
        if not sentence_chunks:
            return text[:800]
        return " ".join(sentence_chunks[:3])[:800]

