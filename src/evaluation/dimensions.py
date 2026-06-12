"""Comparison sweeps for scripts/eval.py, as typed PipelineConfig lists.

Each dimension varies one knob across a set of configs (with a fixed baseline column for
reference). Configs reuse the named presets where they match: BASE is the canonical
dense/MiniLM/k=15 baseline, BEST the hand-stacked winner, NO_RAG the retrieval-off control.
"""

from typing import Any

from src.config import BASE, BEST, NO_RAG, PipelineConfig

DIMENSIONS: dict[str, dict[str, Any]] = {
    "rag_vs_norag": {
        "labels": ["RAG (baseline)", "no-RAG"],
        "configs": [BASE, NO_RAG],
    },
    "retrieval": {
        "labels": ["dense", "bm25", "hybrid-rrf"],
        "configs": [
            BASE,
            PipelineConfig(retriever="bm25"),
            PipelineConfig(retriever="hybrid"),
        ],
    },
    "fusion": {
        "labels": ["hybrid-rrf", "hybrid-weighted"],
        "configs": [
            PipelineConfig(retriever="hybrid", fusion="rrf"),
            PipelineConfig(retriever="hybrid", fusion="weighted"),
        ],
    },
    "reranking": {
        "labels": ["no rerank", "rerank"],
        "configs": [
            BASE,
            PipelineConfig(rerank=True),
        ],
    },
    "embed_model": {
        "labels": ["all-MiniLM-L6-v2", "bge-small-en", "e5-small", "bge-base", "bge-large"],
        "configs": [
            BASE,
            PipelineConfig(embed_model="BAAI/bge-small-en-v1.5"),
            PipelineConfig(embed_model="intfloat/e5-small-v2"),
            PipelineConfig(embed_model="BAAI/bge-base-en-v1.5"),
            PipelineConfig(embed_model="BAAI/bge-large-en-v1.5"),
        ],
    },
    "top_k": {
        "labels": ["top_k=5", "top_k=15", "top_k=20", "top_k=30", "top_k=40", "top_k=60", "top_k=80", "top_k=100"],
        "configs": [
            PipelineConfig(top_k=5),
            BASE,  # top_k=15
            PipelineConfig(top_k=20),
            PipelineConfig(top_k=30),
            PipelineConfig(top_k=40),
            PipelineConfig(top_k=60),
            PipelineConfig(top_k=80),
            PipelineConfig(top_k=100),
        ],
    },
    "chunk_max_tokens": {
        "labels": ["tokens=64", "tokens=128", "tokens=256", "tokens=512", "tokens=1024"],
        "configs": [
            PipelineConfig(chunk_max_tokens=64),
            BASE,  # chunk_max_tokens=128
            PipelineConfig(chunk_max_tokens=256),
            PipelineConfig(chunk_max_tokens=512),
            PipelineConfig(chunk_max_tokens=1024),
        ],
    },
    "best": {
        # Per-dimension winners stacked (BEST) next to the canonical baseline (BASE).
        "labels": ["best-combined", "baseline"],
        "configs": [BEST, BASE],
    },
}
