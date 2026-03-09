from __future__ import annotations

from collections import OrderedDict

from multi_agent_research_assistant.agents.base import BaseAgent
from multi_agent_research_assistant.llm.base import LLMClient
from multi_agent_research_assistant.models import ExtractedInsight, SectionSummary
from multi_agent_research_assistant.tools.text import clean_whitespace, unique_preserve_order

SECTION_MAP: list[tuple[str, str, set[str]]] = [
    (
        "market_overview",
        "Market Overview",
        {"market", "growth", "demand", "adoption", "revenue", "size", "enterprise"},
    ),
    (
        "funding_landscape",
        "Funding Landscape",
        {"funding", "investment", "capital", "round", "venture", "vc", "investor"},
    ),
    (
        "ecosystem_players",
        "Ecosystem Players",
        {"startup", "company", "founder", "hub", "accelerator", "scaleup"},
    ),
    (
        "opportunities",
        "Opportunities",
        {"opportunity", "potential", "expansion", "innovation", "productivity", "advantage"},
    ),
    (
        "risks_constraints",
        "Risks And Constraints",
        {"risk", "challenge", "constraint", "regulation", "compliance", "competition", "cost"},
    ),
    (
        "outlook",
        "Outlook",
        {"outlook", "forecast", "future", "trend", "projection", "roadmap"},
    ),
]


class SummarizationAgent(BaseAgent):
    name = "summarization-agent"

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def run(self, topic: str, insights: list[ExtractedInsight]) -> list[SectionSummary]:
        clean_topic = topic.strip().rstrip(".")
        if not insights:
            return [
                SectionSummary(
                    section_id="market_overview",
                    section_title="Market Overview",
                    narrative=f"No relevant documents were extracted for topic: {clean_topic}.",
                    key_findings=[],
                    numeric_facts=[],
                    citations=[],
                )
            ]

        grouped: OrderedDict[str, list[ExtractedInsight]] = OrderedDict((section_id, []) for section_id, _, _ in SECTION_MAP)
        for insight in insights:
            grouped[self._assign_section(insight)].append(insight)

        summaries: list[SectionSummary] = []
        for section_id, section_title, _keywords in SECTION_MAP:
            items = grouped.get(section_id, [])
            if not items:
                continue
            key_findings = unique_preserve_order(
                [point for insight in items for point in insight.key_points if point]
            )[:8]
            numeric_facts = unique_preserve_order(
                [fact for insight in items for fact in insight.numeric_facts if fact]
            )[:8]
            citations = unique_preserve_order([insight.source_url for insight in items])[:8]

            narrative = self._build_narrative(
                topic=clean_topic,
                section_title=section_title,
                insights=items,
                key_findings=key_findings,
            )
            summaries.append(
                SectionSummary(
                    section_id=section_id,
                    section_title=section_title,
                    narrative=narrative,
                    key_findings=key_findings,
                    numeric_facts=numeric_facts,
                    citations=citations,
                )
            )
        return summaries

    def _assign_section(self, insight: ExtractedInsight) -> str:
        combined = f"{insight.summary} {' '.join(insight.key_points)}".lower()
        scored: list[tuple[int, str]] = []
        for section_id, _title, keywords in SECTION_MAP:
            score = sum(combined.count(keyword) for keyword in keywords)
            scored.append((score, section_id))
        scored.sort(reverse=True)
        best_score, best_section = scored[0]
        if best_score == 0:
            return "market_overview"
        return best_section

    def _build_narrative(
        self,
        topic: str,
        section_title: str,
        insights: list[ExtractedInsight],
        key_findings: list[str],
    ) -> str:
        if self._supports_generative_llm():
            prompt = (
                f"Topic: {topic}\n"
                f"Section: {section_title}\n"
                "Create a concise analytical paragraph based on these findings:\n"
                + "\n".join(f"- {finding}" for finding in key_findings[:8])
            )
            response = clean_whitespace(
                self.llm.generate(prompt=prompt, system_prompt="You write concise market research summaries.")
            )
            if response:
                return response

        lead_finding = key_findings[0] if key_findings else "No key findings available from extracted content."
        return (
            f"{section_title} reflects evidence from {len(insights)} source documents about {topic}. "
            f"The strongest recurring signal is: {lead_finding}"
        )

    def _supports_generative_llm(self) -> bool:
        return getattr(self.llm, "name", "heuristic") != "heuristic"
