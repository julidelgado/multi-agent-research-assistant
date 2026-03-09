from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class WebPage:
    title: str
    text: str


class TrafilaturaWebExtractor:
    def fetch(self, url: str) -> WebPage | None:
        try:
            import trafilatura
        except Exception:
            return None

        try:
            downloaded = trafilatura.fetch_url(url)
        except Exception:
            return None

        if not downloaded:
            return None

        try:
            extracted_text = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=False,
                favor_precision=True,
                deduplicate=True,
            )
            metadata = trafilatura.extract_metadata(downloaded)
        except Exception:
            return None

        if not extracted_text:
            return None

        title = ""
        if metadata and getattr(metadata, "title", None):
            title = metadata.title.strip()

        return WebPage(title=title or url, text=extracted_text.strip())
