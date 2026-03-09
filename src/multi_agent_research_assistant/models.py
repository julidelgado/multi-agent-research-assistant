from __future__ import annotations

from datetime import datetime, timezone
from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    query: str
    title: str
    url: str
    snippet: str = ""
    source: str = "duckduckgo"


class ResearchPackage(BaseModel):
    topic: str
    queries: list[str]
    search_results: list[SearchResult]


class ResearchDocument(BaseModel):
    query: str
    title: str
    url: str
    snippet: str = ""
    content: str


class ExtractedInsight(BaseModel):
    source_url: str
    source_title: str
    summary: str
    key_points: list[str]
    numeric_facts: list[str]
    relevance_score: float = Field(ge=0.0, le=1.0)


class ExtractionPackage(BaseModel):
    documents: list[ResearchDocument]
    insights: list[ExtractedInsight]
    skipped_urls: list[str] = Field(default_factory=list)


class SectionSummary(BaseModel):
    section_id: str
    section_title: str
    narrative: str
    key_findings: list[str] = Field(default_factory=list)
    numeric_facts: list[str] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)


class ReportSection(BaseModel):
    title: str
    narrative: str
    bullet_points: list[str] = Field(default_factory=list)
    numeric_facts: list[str] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)


class FinalReport(BaseModel):
    topic: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    executive_summary: str
    sections: list[ReportSection]
    conclusion: str
    sources: list[str]

    def to_markdown(self) -> str:
        lines: list[str] = [
            f"# Research Report: {self.topic}",
            "",
            f"_Generated: {self.generated_at.isoformat(timespec='seconds')}_",
            "",
            "## Executive Summary",
            self.executive_summary,
            "",
        ]

        for section in self.sections:
            lines.extend([f"## {section.title}", section.narrative, ""])
            if section.bullet_points:
                lines.append("### Key Findings")
                lines.extend(f"- {finding}" for finding in section.bullet_points)
                lines.append("")
            if section.numeric_facts:
                lines.append("### Numeric Evidence")
                lines.extend(f"- {fact}" for fact in section.numeric_facts)
                lines.append("")
            if section.citations:
                lines.append("### Sources")
                lines.extend(f"- {citation}" for citation in section.citations)
                lines.append("")

        lines.extend(["## Conclusion", self.conclusion, "", "## All Sources"])
        lines.extend(f"- {source}" for source in self.sources)
        lines.append("")
        return "\n".join(lines)


class WorkflowArtifacts(BaseModel):
    research: ResearchPackage
    extraction: ExtractionPackage
    section_summaries: list[SectionSummary]
    report: FinalReport

