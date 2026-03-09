from __future__ import annotations

from multi_agent_research_assistant.agents.extraction_agent import ExtractionAgent
from multi_agent_research_assistant.agents.report_generation_agent import ReportGenerationAgent
from multi_agent_research_assistant.agents.research_agent import ResearchAgent
from multi_agent_research_assistant.agents.summarization_agent import SummarizationAgent
from multi_agent_research_assistant.config import Settings
from multi_agent_research_assistant.llm.heuristic import HeuristicLLMClient
from multi_agent_research_assistant.models import SearchResult
from multi_agent_research_assistant.orchestrator import MultiAgentResearchAssistant
from multi_agent_research_assistant.tools.web import WebPage


class FakeSearchTool:
    def search(self, query: str, max_results: int = 8) -> list[SearchResult]:
        if "funding" in query.lower():
            return [
                SearchResult(
                    query=query,
                    title="Funding Update",
                    url="https://example.com/funding",
                    snippet="Funding has grown quickly across EU hubs.",
                )
            ]
        return [
            SearchResult(
                query=query,
                title="Market Overview",
                url="https://example.com/market",
                snippet="AI startup market continues to expand.",
            )
        ]


class FakeWebExtractor:
    def fetch(self, url: str) -> WebPage | None:
        if "funding" in url:
            return WebPage(
                title="Funding Update",
                text=(
                    "AI startup funding in Europe reached EUR 2.8 billion in 2025. "
                    "Several rounds above EUR 100 million were recorded. "
                    "Investors highlighted applied AI demand in finance and healthcare sectors."
                ),
            )
        return WebPage(
            title="Market Overview",
            text=(
                "The European AI startup market keeps expanding with new hubs in Spain and Germany. "
                "Enterprise adoption improved across manufacturing and retail. "
                "Regulatory clarity remains a challenge for fast-growing companies."
            ),
        )


def test_pipeline_generates_structured_report():
    settings = Settings(
        llm_provider="heuristic",
        max_queries=3,
        max_results_per_query=3,
        max_documents=4,
        min_document_chars=80,
    )
    llm = HeuristicLLMClient()
    assistant = MultiAgentResearchAssistant(
        research_agent=ResearchAgent(FakeSearchTool(), llm, settings),
        extraction_agent=ExtractionAgent(FakeWebExtractor(), llm, settings),
        summarization_agent=SummarizationAgent(llm),
        report_agent=ReportGenerationAgent(llm),
    )

    artifacts = assistant.run(topic="AI startup market in Europe")

    assert artifacts.research.queries
    assert artifacts.extraction.documents
    assert artifacts.section_summaries
    assert artifacts.report.sections
    markdown = artifacts.report.to_markdown()
    assert "## Executive Summary" in markdown
    assert "## Conclusion" in markdown

