"""Evaluation data and config shared by scripts/benchmark.py and the API evaluate path.

Holds the QA_PAIRS question set and the path of the shared LLM answer cache. The cache lives
under env.CACHE_DIR so it is cleared
together with the embedding/index caches when the corpus changes (the API's clear_all_cache).
"""

from pathlib import Path

from src.config import env

ANSWER_CACHE_PATH = Path(env.CACHE_DIR) / "answers.json"
