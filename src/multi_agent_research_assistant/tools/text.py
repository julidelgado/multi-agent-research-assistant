from __future__ import annotations

import re
import unicodedata

try:
    from ftfy import fix_text
except Exception:  # pragma: no cover
    fix_text = None

_STOP_WORDS = {
    "a",
    "about",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "market",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "with",
}

_WHITESPACE_RE = re.compile(r"\s+")
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_NUMBER_RE = re.compile(
    r"\b(?:\d{1,3}(?:[.,]\d{3})+|\d+(?:[.,]\d+)?)\s?(?:%|percent|bn|billion|million|m|k|eur|usd|gbp|euro|dollars?)?\b",
    re.IGNORECASE,
)
_MOJIBAKE_MAP = {
    "â€™": "'",
    "â€˜": "'",
    "â€œ": '"',
    "â€\x9d": '"',
    "â€“": "-",
    "â€”": "-",
    "â€¦": "...",
    "â‚¬": "EUR ",
}


def clean_whitespace(value: str) -> str:
    normalized = value
    if fix_text is not None:
        normalized = fix_text(normalized)
    for bad, good in _MOJIBAKE_MAP.items():
        normalized = normalized.replace(bad, good)
    return _WHITESPACE_RE.sub(" ", normalized).strip()


def split_sentences(text: str) -> list[str]:
    cleaned = clean_whitespace(text)
    if not cleaned:
        return []
    return [sentence.strip() for sentence in _SENTENCE_SPLIT_RE.split(cleaned) if sentence.strip()]


def topic_keywords(topic: str) -> list[str]:
    normalized = unicodedata.normalize("NFKD", topic).lower()
    tokens = [token for token in re.findall(r"[a-z0-9]{3,}", normalized) if token not in _STOP_WORDS]
    return unique_preserve_order(tokens)


def top_relevant_sentences(text: str, keywords: list[str], limit: int = 5) -> list[str]:
    candidates = split_sentences(text)
    if not candidates:
        return []
    if not keywords:
        return candidates[:limit]

    scored: list[tuple[float, str]] = []
    for sentence in candidates:
        lowered = sentence.lower()
        score = float(sum(lowered.count(keyword) for keyword in keywords))
        if any(char.isdigit() for char in sentence):
            score += 0.5
        if score > 0:
            scored.append((score, sentence))

    if not scored:
        return candidates[:limit]
    scored.sort(key=lambda pair: (pair[0], len(pair[1])), reverse=True)
    return unique_preserve_order([sentence for _, sentence in scored])[:limit]


def extract_numeric_facts(text: str, limit: int = 6) -> list[str]:
    sentences = split_sentences(text)
    findings: list[str] = []
    for sentence in sentences:
        if _NUMBER_RE.search(sentence):
            findings.append(clean_whitespace(sentence))
        if len(findings) >= limit:
            break
    return unique_preserve_order(findings)[:limit]


def unique_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value not in seen:
            ordered.append(value)
            seen.add(value)
    return ordered


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_value).strip("-").lower()
    return cleaned or "report"
