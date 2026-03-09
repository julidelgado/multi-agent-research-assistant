from __future__ import annotations

from datetime import datetime, timezone

from multi_agent_research_assistant.agents.base import BaseAgent
from multi_agent_research_assistant.llm.base import LLMClient
from multi_agent_research_assistant.models import (
    FinalReport,
    ReportSection,
    ResearchDocument,
    SectionSummary,
)
from multi_agent_research_assistant.tools.text import clean_whitespace, unique_preserve_order


class ReportGenerationAgent(BaseAgent):
    name = "report-generation-agent"

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def run(
        self,
        topic: str,
        section_summaries: list[SectionSummary],
        documents: list[ResearchDocument],
    ) -> FinalReport:
        clean_topic = topic.strip().rstrip(".")
        report_sections = [
            ReportSection(
                title=section.section_title,
                narrative=section.narrative,
                bullet_points=section.key_findings[:8],
                numeric_facts=section.numeric_facts[:8],
                citations=section.citations[:8],
            )
            for section in section_summaries
        ]

        executive_summary = self._build_executive_summary(clean_topic, report_sections)
        conclusion = self._build_conclusion(clean_topic, report_sections)
        sources = unique_preserve_order([doc.url for doc in documents])

        return FinalReport(
            topic=clean_topic,
            generated_at=datetime.now(timezone.utc),
            executive_summary=executive_summary,
            sections=report_sections,
            conclusion=conclusion,
            sources=sources,
        )

    def _build_executive_summary(self, topic: str, sections: list[ReportSection]) -> str:
        if not sections:
            return f"No report sections were generated for topic: {topic}."

        distilled_findings = unique_preserve_order(
            [finding for section in sections for finding in section.bullet_points]
        )[:4]
        if self._supports_generative_llm() and distilled_findings:
            prompt = (
                f"Topic: {topic}\n"
                "Write an executive summary paragraph from the findings below:\n"
                + "\n".join(f"- {finding}" for finding in distilled_findings)
            )
            generated = clean_whitespace(
                self.llm.generate(prompt=prompt, system_prompt="You produce concise market intelligence summaries.")
            )
            if generated:
                return generated

        summary_parts = [
            f"This report analyzes {topic} using a multi-agent workflow over web sources.",
            f"It synthesizes {len(sections)} analytical sections.",
        ]
        if distilled_findings:
            summary_parts.append(f"Leading signal: {distilled_findings[0]}")
        return " ".join(summary_parts)

    def _build_conclusion(self, topic: str, sections: list[ReportSection]) -> str:
        if not sections:
            return f"Further data collection is required to conclude on {topic}."

        opportunities = self._find_section(sections, "Opportunities")
        risks = self._find_section(sections, "Risks")

        if self._supports_generative_llm():
            prompt = (
                f"Topic: {topic}\n"
                "Write a balanced conclusion with strategic recommendations using this context:\n"
                f"Opportunities: {'; '.join(opportunities[:4])}\n"
                f"Risks: {'; '.join(risks[:4])}"
            )
            generated = clean_whitespace(
                self.llm.generate(prompt=prompt, system_prompt="You produce balanced, practical conclusions.")
            )
            if generated:
                return generated

        opportunity_text = opportunities[0] if opportunities else "clear expansion opportunities"
        risk_text = risks[0] if risks else "execution and regulatory risks"
        return (
            f"The {topic} landscape in Europe shows momentum but remains uneven across segments and geographies. "
            f"Teams entering this market should prioritize areas where {opportunity_text} while mitigating {risk_text}."
        )

    @staticmethod
    def _find_section(sections: list[ReportSection], prefix: str) -> list[str]:
        for section in sections:
            if section.title.lower().startswith(prefix.lower()):
                return section.bullet_points
        return []

    def _supports_generative_llm(self) -> bool:
        return getattr(self.llm, "name", "heuristic") != "heuristic"
