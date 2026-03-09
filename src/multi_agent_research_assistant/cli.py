from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from multi_agent_research_assistant.config import Settings
from multi_agent_research_assistant.orchestrator import MultiAgentResearchAssistant
from multi_agent_research_assistant.tools.text import slugify


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="multi-agent-research",
        description="Multi-Agent Research Assistant: web research to structured report.",
    )
    parser.add_argument("topic", nargs="+", help='Research prompt, e.g. "Analyze the AI startup market in Europe."')
    parser.add_argument("--output-dir", default="reports", help="Directory to save generated reports.")
    parser.add_argument("--format", choices=["markdown", "json", "both"], default="both")
    parser.add_argument("--provider", choices=["heuristic", "ollama"], default=None)
    parser.add_argument("--ollama-model", default=None)
    parser.add_argument("--ollama-base-url", default=None)
    parser.add_argument("--max-queries", type=int, default=None)
    parser.add_argument("--max-results-per-query", type=int, default=None)
    parser.add_argument("--max-documents", type=int, default=None)
    parser.add_argument("--min-document-chars", type=int, default=None)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    topic = " ".join(args.topic).strip()

    settings = Settings.from_env().with_overrides(
        llm_provider=args.provider,
        ollama_model=args.ollama_model,
        ollama_base_url=args.ollama_base_url,
        max_queries=args.max_queries,
        max_results_per_query=args.max_results_per_query,
        max_documents=args.max_documents,
        min_document_chars=args.min_document_chars,
    )

    assistant = MultiAgentResearchAssistant.from_settings(settings)
    artifacts = assistant.run(
        topic=topic,
        max_queries=settings.max_queries,
        max_results_per_query=settings.max_results_per_query,
        max_documents=settings.max_documents,
        min_document_chars=settings.min_document_chars,
    )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    base_name = f"{timestamp}-{slugify(topic)}"

    saved_paths: list[Path] = []
    if args.format in {"markdown", "both"}:
        markdown_path = output_dir / f"{base_name}.md"
        markdown_path.write_text(artifacts.report.to_markdown(), encoding="utf-8")
        saved_paths.append(markdown_path)

    if args.format in {"json", "both"}:
        json_path = output_dir / f"{base_name}.json"
        json_path.write_text(artifacts.report.model_dump_json(indent=2), encoding="utf-8")
        saved_paths.append(json_path)

    print("Multi-Agent Research Assistant completed.")
    print(f"Topic: {topic}")
    print(f"Queries used: {len(artifacts.research.queries)}")
    print(f"Search results collected: {len(artifacts.research.search_results)}")
    print(f"Documents analyzed: {len(artifacts.extraction.documents)}")
    print("Outputs:")
    for path in saved_paths:
        print(f"- {path.resolve()}")


if __name__ == "__main__":
    main()

