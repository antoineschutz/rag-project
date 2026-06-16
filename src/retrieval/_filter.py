"""Source-filter helpers shared by the retrievers.

Qdrant filters natively via a payload filter and cosine masks indices directly; FAISS and
BM25 widen their candidate pool then drop non-matching sources with `filter_by_source`.
"""

from typing import Any


def normalize_sources(source: str | list[str] | None) -> set[str] | None:
    """Return the allowed-source set, or None when no filter is requested."""
    if source is None:
        return None
    if isinstance(source, str):
        return {source}
    return set(source)


def filter_by_source(
    results: list[dict[str, Any]], source: str | list[str] | None
) -> list[dict[str, Any]]:
    """Drop results whose source is not in the allowed set (no-op when source is None)."""
    allowed = normalize_sources(source)
    if allowed is None:
        return results
    return [r for r in results if r["source"] in allowed]
