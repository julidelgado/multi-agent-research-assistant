from __future__ import annotations

import base64
try:
    from ddgs import DDGS
except Exception:  # pragma: no cover
    from duckduckgo_search import DDGS  # type: ignore[no-redef]
from urllib.parse import parse_qs, unquote, urlparse

from multi_agent_research_assistant.models import SearchResult


def normalize_search_url(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.scheme.startswith("http"):
        return ""

    hostname = parsed.netloc.lower()
    query_params = parse_qs(parsed.query)

    # DuckDuckGo redirect wrapper.
    if "duckduckgo.com" in hostname and parsed.path.startswith("/l/"):
        target = query_params.get("uddg", [""])[0]
        return unquote(target).strip() if target else ""

    # Bing click tracking redirect wrapper.
    if "bing.com" in hostname and parsed.path.startswith("/aclick"):
        target = query_params.get("u", [""])[0]
        if not target:
            return ""
        target = unquote(target)
        if target.startswith(("http://", "https://")):
            return target
        try:
            padding = "=" * (-len(target) % 4)
            decoded = base64.b64decode(target + padding).decode("utf-8", errors="ignore")
            if decoded.startswith(("http://", "https://")):
                return decoded
        except Exception:
            return ""
        return ""

    return url


class DuckDuckGoSearchTool:
    def __init__(self, region: str = "wt-wt", safesearch: str = "moderate"):
        self.region = region
        self.safesearch = safesearch

    def search(self, query: str, max_results: int = 8) -> list[SearchResult]:
        output: list[SearchResult] = []
        try:
            with DDGS() as ddgs:
                results = ddgs.text(
                    query,
                    region=self.region,
                    safesearch=self.safesearch,
                    max_results=max_results,
                )
                for item in results:
                    raw_url = item.get("href") or item.get("url") or ""
                    url = normalize_search_url(raw_url.strip())
                    if "bing.com/aclick" in url:
                        continue
                    if not url:
                        continue
                    output.append(
                        SearchResult(
                            query=query,
                            title=(item.get("title") or "").strip() or url,
                            url=url.strip(),
                            snippet=(item.get("body") or "").strip(),
                            source="duckduckgo",
                        )
                    )
        except Exception:
            return []
        return output
