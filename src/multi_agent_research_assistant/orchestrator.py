from __future__ import annotations

from multi_agent_research_assistant.agents.extraction_agent import ExtractionAgent
from multi_agent_research_assistant.agents.report_generation_agent import ReportGenerationAgent
from multi_agent_research_assistant.agents.research_agent import ResearchAgent
from multi_agent_research_assistant.agents.summarization_agent import SummarizationAgent
from multi_agent_research_assistant.config import Settings
from multi_agent_research_assistant.llm.factory import build_llm_client
from multi_agent_research_assistant.models import WorkflowArtifacts
from multi_agent_research_assistant.tools.search import DuckDuckGoSearchTool
from multi_agent_research_assistant.tools.web import TrafilaturaWebExtractor


class MultiAgentResearchAssistant:
    def __init__(
        self,
        research_agent: ResearchAgent,
        extraction_agent: ExtractionAgent,
        summarization_agent: SummarizationAgent,
        report_agent: ReportGenerationAgent,
    ):
        self.research_agent = research_agent
        self.extraction_agent = extraction_agent
        self.summarization_agent = summarization_agent
        self.report_agent = report_agent

    @classmethod
    def from_settings(cls, settings: Settings | None = None) -> "MultiAgentResearchAssistant":
        effective_settings = settings or Settings.from_env()
        llm = build_llm_client(effective_settings)
        return cls(
            research_agent=ResearchAgent(
                search_tool=DuckDuckGoSearchTool(),
                llm=llm,
                settings=effective_settings,
            ),
            extraction_agent=ExtractionAgent(
                web_extractor=TrafilaturaWebExtractor(),
                llm=llm,
                settings=effective_settings,
            ),
            summarization_agent=SummarizationAgent(llm=llm),
            report_agent=ReportGenerationAgent(llm=llm),
        )

    def run(
        self,
        topic: str,
        max_queries: int | None = None,
        max_results_per_query: int | None = None,
        max_documents: int | None = None,
        min_document_chars: int | None = None,
    ) -> WorkflowArtifacts:
        research_package = self.research_agent.run(
            topic=topic,
            max_queries=max_queries,
            max_results_per_query=max_results_per_query,
        )
        extraction_package = self.extraction_agent.run(
            topic=topic,
            search_results=research_package.search_results,
            max_documents=max_documents,
            min_document_chars=min_document_chars,
        )
        section_summaries = self.summarization_agent.run(
            topic=topic,
            insights=extraction_package.insights,
        )
        report = self.report_agent.run(
            topic=topic,
            section_summaries=section_summaries,
            documents=extraction_package.documents,
        )
        return WorkflowArtifacts(
            research=research_package,
            extraction=extraction_package,
            section_summaries=section_summaries,
            report=report,
        )

