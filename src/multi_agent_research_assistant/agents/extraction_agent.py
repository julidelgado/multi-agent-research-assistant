from __future__ import annotations

from multi_agent_research_assistant.agents.base import BaseAgent
from multi_agent_research_assistant.config import Settings
from multi_agent_research_assistant.llm.base import LLMClient
from multi_agent_research_assistant.models import (
    ExtractedInsight,
    ExtractionPackage,
    ResearchDocument,
    SearchResult,
)
from multi_agent_research_assistant.tools.text import (
    clean_whitespace,
    extract_numeric_facts,
    top_relevant_sentences,
    topic_keywords,
    unique_preserve_order,
)
from multi_agent_research_assistant.tools.web import TrafilaturaWebExtractor


class ExtractionAgent(BaseAgent):
    name = "extraction-agent"

    def __init__(self, web_extractor: TrafilaturaWebExtractor, llm: LLMClient, settings: Settings):
        self.web_extractor = web_extractor
        self.llm = llm
        self.settings = settings

    def run(
        self,
        topic: str,
        search_results: list[SearchResult],
        max_documents: int | None = None,
        min_document_chars: int | None = None,
    ) -> ExtractionPackage:
        doc_limit = max_documents or self.settings.max_documents
        min_chars = min_document_chars or self.settings.min_document_chars

        documents: list[ResearchDocument] = []
        insights: list[ExtractedInsight] = []
        skipped_urls: list[str] = []

        for result in search_results:
            if len(documents) >= doc_limit:
                break
            webpage = self.web_extractor.fetch(result.url)
            if webpage is None:
                skipped_urls.append(result.url)
                continue

            content = clean_whitespace(webpage.text)
            if len(content) < min_chars:
                skipped_urls.append(result.url)
                continue

            document = ResearchDocument(
                query=result.query,
                title=webpage.title or result.title,
                url=result.url,
                snippet=result.snippet,
                content=content,
            )
            documents.append(document)
            insights.append(self._extract_insight(topic=topic, document=document))

        return ExtractionPackage(
            documents=documents,
            insights=insights,
            skipped_urls=unique_preserve_order(skipped_urls),
        )

    def _extract_insight(self, topic: str, document: ResearchDocument) -> ExtractedInsight:
        keywords = topic_keywords(topic)
        top_sentences = top_relevant_sentences(document.content, keywords, limit=5)
        summary = " ".join(top_sentences[:2]).strip()
        if not summary:
            summary = document.snippet or document.content[:240]

        key_points = top_sentences[:5] if top_sentences else [summary]
        numeric_facts = extract_numeric_facts(document.content, limit=6)
        relevance_score = self._calculate_relevance(document.content, keywords)

        return ExtractedInsight(
            source_url=document.url,
            source_title=document.title,
            summary=summary,
            key_points=key_points,
            numeric_facts=numeric_facts,
            relevance_score=relevance_score,
        )

    @staticmethod
    def _calculate_relevance(text: str, keywords: list[str]) -> float:
        if not text or not keywords:
            return 0.0
        lowered = text.lower()
        hit_count = sum(lowered.count(keyword) for keyword in keywords)
        normalized = min(1.0, hit_count / max(6, len(keywords) * 3))
        return round(normalized, 3)

