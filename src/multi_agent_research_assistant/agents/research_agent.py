from __future__ import annotations

from multi_agent_research_assistant.agents.base import BaseAgent
from multi_agent_research_assistant.config import Settings
from multi_agent_research_assistant.llm.base import LLMClient
from multi_agent_research_assistant.models import ResearchPackage, SearchResult
from multi_agent_research_assistant.tools.search import DuckDuckGoSearchTool
from multi_agent_research_assistant.tools.text import unique_preserve_order


class ResearchAgent(BaseAgent):
    name = "research-agent"

    def __init__(self, search_tool: DuckDuckGoSearchTool, llm: LLMClient, settings: Settings):
        self.search_tool = search_tool
        self.llm = llm
        self.settings = settings

    def run(
        self,
        topic: str,
        max_queries: int | None = None,
        max_results_per_query: int | None = None,
    ) -> ResearchPackage:
        query_limit = max_queries or self.settings.max_queries
        result_limit = max_results_per_query or self.settings.max_results_per_query

        queries = self._build_queries(topic, max_queries=query_limit)
        all_results: list[SearchResult] = []
        seen_urls: set[str] = set()

        for query in queries:
            results = self.search_tool.search(query, max_results=result_limit)
            for result in results:
                if result.url in seen_urls:
                    continue
                seen_urls.add(result.url)
                all_results.append(result)

        return ResearchPackage(topic=topic, queries=queries, search_results=all_results)

    def _build_queries(self, topic: str, max_queries: int) -> list[str]:
        default_queries = [
            f"{topic} Europe market size trends 2025 2026",
            f"{topic} Europe startup funding venture capital",
            f"{topic} top startups Europe country breakdown",
            f"{topic} regulations policy Europe startups",
            f"{topic} opportunities risks Europe market outlook",
            f"{topic} enterprise adoption Europe case studies",
        ]

        generated_queries: list[str] = []
        if self._supports_generative_llm():
            prompt = (
                "Create 6 focused web-search queries for market research.\n"
                f"Topic: {topic}\n"
                "Focus on Europe and include: market size, funding, players, regulations, risks, forecast.\n"
                "Return one query per line with no numbering."
            )
            raw = self.llm.generate(prompt=prompt, system_prompt="You are a market research strategist.")
            for line in raw.splitlines():
                candidate = line.strip(" -0123456789.").strip()
                if len(candidate) > 8:
                    generated_queries.append(candidate)

        merged = unique_preserve_order(default_queries + generated_queries)
        return merged[:max_queries]

    def _supports_generative_llm(self) -> bool:
        return getattr(self.llm, "name", "heuristic") != "heuristic"

