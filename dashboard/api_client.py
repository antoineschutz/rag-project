"""HTTP client the Streamlit dashboard uses to talk to the FastAPI server.

Each call returns parsed JSON or raises APIError with a message suitable for showing to the
user (st.error) instead of a raw traceback. The server base URL is read from RAG_API_URL
(default http://127.0.0.1:8000).
"""

import json
import os
from collections.abc import Iterator
from typing import Any

import requests

API_URL = os.environ.get("RAG_API_URL", "http://127.0.0.1:8000").rstrip("/")

# /health and /presets are quick; a single /query runs the LLM (and maybe reranking), so it
# needs a generous timeout; /compare runs two; /evaluate covers the whole question set.
DEFAULT_TIMEOUT = 30.0
QUERY_TIMEOUT = 300.0
COMPARE_TIMEOUT = 600.0
EVALUATE_TIMEOUT = 1800.0


class APIError(RuntimeError):
    """A request to the API failed (unreachable, timed out, or non-200). Message is user-facing."""


def _request(method: str, path: str, *, timeout: float = DEFAULT_TIMEOUT, **kwargs: Any) -> Any:
    """Send one request and return parsed JSON, mapping any failure to a friendly APIError."""
    url = f"{API_URL}{path}"
    try:
        resp = requests.request(method, url, timeout=timeout, **kwargs)
    except requests.exceptions.ConnectionError as exc:
        raise APIError(
            f"API not reachable at {API_URL}. Start it with `uvicorn src.api.server:app`."
        ) from exc
    except requests.exceptions.Timeout as exc:
        raise APIError(f"API request to {path} timed out after {timeout:.0f}s.") from exc

    if resp.status_code != 200:
        # FastAPI puts validation/HTTP errors under "detail"; fall back to the raw body.
        try:
            detail = resp.json().get("detail", resp.text)
        except ValueError:
            detail = resp.text
        raise APIError(f"API error {resp.status_code}: {detail}")
    return resp.json()


def health() -> bool:
    """Return True if the server answers /health, False if it is unreachable."""
    try:
        return _request("GET", "/health", timeout=5.0).get("status") == "ok"
    except APIError:
        return False


# The dashboard exposes a curated subset of the server's presets (the rest are eval-only).
DASHBOARD_PRESETS = ("baseline", "best", "gpt", "llama3.1-8b")


def get_presets() -> dict[str, dict[str, Any]]:
    """Return the dashboard's curated presets (name -> flat config dict) from /presets."""
    all_presets = _request("GET", "/presets")
    return {name: all_presets[name] for name in DASHBOARD_PRESETS if name in all_presets}


def get_sources() -> list[str]:
    """Return the available document sources (filenames) from /sources."""
    return _request("GET", "/sources")


def post_query(
    query: str, config: str | dict[str, Any] | None,
    history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Run one query. `config` is a preset name, inline knob dict, or None (best preset).

    `history` is the prior chat turns (each {role, content}) for multi-turn; omit for single-shot.
    """
    return _request(
        "POST", "/query",
        json={"query": query, "config": config, "history": history}, timeout=QUERY_TIMEOUT,
    )


def post_query_stream(
    query: str, config: str | dict[str, Any] | None,
    history: list[dict[str, str]] | None = None,
) -> tuple[dict[str, Any], Iterator[str]]:
    """Run one query against /query/stream. Return (meta, tokens).

    meta holds chunks/config/hyde_doc/standalone_query (received before generation starts); tokens
    yields the answer text chunks as they arrive. `history` is the prior chat turns (each
    {role, content}) for multi-turn; omit for single-shot. Raises APIError on connection/timeout/
    non-200, or if the server reports an error event.
    """
    url = f"{API_URL}/query/stream"
    try:
        resp = requests.post(
            url,
            json={"query": query, "config": config, "history": history},
            stream=True, timeout=QUERY_TIMEOUT,
        )
    except requests.exceptions.ConnectionError as exc:
        raise APIError(
            f"API not reachable at {API_URL}. Start it with `uvicorn src.api.server:app`."
        ) from exc
    except requests.exceptions.Timeout as exc:
        raise APIError(f"API request to /query/stream timed out after {QUERY_TIMEOUT:.0f}s.") from exc

    if resp.status_code != 200:
        try:
            detail = resp.json().get("detail", resp.text)
        except ValueError:
            detail = resp.text
        raise APIError(f"API error {resp.status_code}: {detail}")

    lines = resp.iter_lines(decode_unicode=True)
    meta: dict[str, Any] | None = None
    for raw in lines:
        if not raw:
            continue
        event = json.loads(raw)
        if event.get("type") == "error":
            raise APIError(f"API error: {event.get('detail')}")
        if event.get("type") == "meta":
            meta = event
            break
    if meta is None:
        raise APIError("Stream ended before any data was received.")

    def tokens() -> Iterator[str]:
        for raw in lines:
            if not raw:
                continue
            event = json.loads(raw)
            if event.get("type") == "token":
                yield event["text"]
            elif event.get("type") == "error":
                raise APIError(f"API error: {event.get('detail')}")

    return meta, tokens()


def post_compare(
    query: str, a: str | dict[str, Any], b: str | dict[str, Any]
) -> dict[str, Any]:
    """Run one query through two configs (preset names or inline dicts) side by side."""
    return _request("POST", "/compare", json={"query": query, "a": a, "b": b}, timeout=COMPARE_TIMEOUT)


def post_evaluate(
    name: str, config: dict[str, Any] | None = None, fresh: bool = False, judge: bool = False
) -> dict[str, Any]:
    """Score a config over the QA set. A known preset `name` wins over `config` (server side)."""
    payload = {"name": name, "config": config, "fresh": fresh, "judge": judge}
    return _request("POST", "/evaluate", json=payload, timeout=EVALUATE_TIMEOUT)
