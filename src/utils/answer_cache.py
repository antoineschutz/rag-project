"""Disk-backed cache of LLM answers, keyed by (query, config).

Used by the eval/benchmark tooling to skip regenerating an answer that was already produced
for the same question and pipeline config. The mechanism is generic; the caller supplies the
file path (the eval tooling uses ANSWER_CACHE_PATH in src/evaluation).
"""

import hashlib
import json
from pathlib import Path
from typing import Any


class AnswerCache:
    """A json dict on disk mapping key(query, cfg) -> answer string.

    The whole dict is loaded once at construction and rewritten on each `set` (the answer
    set is small, so this stays simple). `key` is a static method so callers can compute a
    key without holding an instance.
    """

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self._data: dict[str, str] = self._load()

    def _load(self) -> dict[str, str]:
        if self.path.exists():
            return json.loads(self.path.read_text())
        return {}

    @staticmethod
    def key(query: str, cfg: dict[str, Any]) -> str:
        """Stable hash of the question and the (flattened) config dict."""
        payload = json.dumps({"query": query, "cfg": cfg}, sort_keys=True)
        return hashlib.md5(payload.encode()).hexdigest()

    def get(self, key: str) -> str | None:
        return self._data.get(key)

    def set(self, key: str, answer: str) -> None:
        self._data[key] = answer
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._data, indent=2))
