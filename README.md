# Multi-Agent Research Assistant

Free multi-agent research system that takes a prompt like:

`Analyze the AI startup market in Europe.`

and outputs a full structured report (`.md` and `.json`).

## What Was Built

This implementation uses 4 collaborating agents:

1. `Research Agent`  
Generates focused queries and collects web search results (DuckDuckGo).

2. `Data Extraction Agent`  
Fetches and extracts clean article text (Trafilatura), then creates structured insights.

3. `Summarization Agent`  
Groups insights into analytical sections (market, funding, players, opportunities, risks, outlook).

4. `Report Generation Agent`  
Builds executive summary, section narratives, numeric evidence, and conclusion.

## Tech Stack (Free)

- `Python 3.11+`
- `ddgs` for free web search
- `trafilatura` for content extraction
- `pydantic` for structured schemas
- Optional: `ollama` (local free model) for stronger generation
- Built-in heuristic mode (no model required)

## Pipeline Phases Implemented

1. Project scaffolding and configuration
2. Core schemas + LLM abstraction + research tools
3. Multi-agent workflow implementation
4. CLI and report artifact generation
5. Tests and documentation
6. Validation via `pytest` and smoke run

## Setup

Linux / WSL:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Windows PowerShell:

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
py -3 -m pip install -e .[dev]
```

## Run

```bash
python3 -m multi_agent_research_assistant "Analyze the AI startup market in Europe."
```

Windows PowerShell:

```powershell
py -3 -m multi_agent_research_assistant "Analyze the AI startup market in Europe."
```

Outputs are written by default to `reports/`.

## CLI Options

```bash
multi-agent-research "Your topic" \
  --output-dir reports \
  --format both \
  --provider heuristic \
  --max-queries 5 \
  --max-results-per-query 8 \
  --max-documents 10 \
  --min-document-chars 800
```

### Use Local Ollama (optional)

```bash
multi-agent-research "Analyze the AI startup market in Europe." \
  --provider ollama \
  --ollama-model llama3.1:8b \
  --ollama-base-url http://localhost:11434
```

If Ollama is unavailable, the app automatically falls back to heuristic mode.

## Environment Variables

Copy `.env.example` and set values as needed:

- `MARA_LLM_PROVIDER`
- `MARA_OLLAMA_BASE_URL`
- `MARA_OLLAMA_MODEL`
- `MARA_MAX_QUERIES`
- `MARA_MAX_RESULTS_PER_QUERY`
- `MARA_MAX_DOCUMENTS`
- `MARA_MIN_DOCUMENT_CHARS`

## Project Structure

```text
src/multi_agent_research_assistant/
  agents/
  llm/
  tools/
  cli.py
  config.py
  models.py
  orchestrator.py
tests/
reports/
```

## Test

```bash
pytest
```

## License

This project is licensed under the MIT License. See `LICENSE`.
