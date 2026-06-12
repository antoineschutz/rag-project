"""The pipeline configuration: the PipelineConfig schema, the default (BASE), and the
named presets that build on it.

A preset is just a complete PipelineConfig. BASE = PipelineConfig() is the default pipeline
(it is the "baseline" preset) and the single source the param-group defaults (src/config/params.py)
and the low-level function defaults (Embedder, chunking, retrieve) draw from. Fields are
lower_snake so asdict() yields the flat config dicts the pipeline consumes (IndexParams.from_dict
etc.). `as_config_dict` flattens a PipelineConfig (or passes a dict through).
"""

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class PipelineConfig:
    """A complete pipeline configuration (i.e. a preset): every tunable knob with a default."""

    retriever: str = "dense"  # dense | bm25 | hybrid
    store: str = "numpy"  # numpy | faiss
    index_type: str = "flat"  # flat | ivf
    embed_model: str = "all-MiniLM-L6-v2"
    chunk_max_tokens: int = 128
    chunk_overlap: int = 50
    top_k: int = 15
    rerank: bool = False
    hyde: bool = False
    fusion: str = "rrf"  # rrf | weighted (hybrid only)
    alpha: float = 0.5  # dense weight for weighted fusion (hybrid only)
    no_rag: bool = False
    backend: str | None = None  # None defers to env.LLM_BACKEND in LLMClient
    model: str | None = None  # None defers to the env model for the backend
    num_ctx: int | None = None  # None defers to env.OLLAMA_NUM_CTX


BASE = PipelineConfig()
BEST = PipelineConfig(
    retriever="hybrid", fusion="rrf", alpha=0.5,
    embed_model="BAAI/bge-small-en-v1.5", rerank=True, top_k=20, chunk_max_tokens=128,
)
NO_RAG = PipelineConfig(no_rag=True)

PRESETS: dict[str, PipelineConfig] = {
    "no-rag": NO_RAG,
    "baseline": BASE,  # the default pipeline is the baseline preset
    "best": BEST,
}


def as_config_dict(cfg: PipelineConfig | dict[str, Any]) -> dict[str, Any]:
    """Flatten a PipelineConfig to a kwargs dict; pass an already-flat dict through unchanged."""
    return asdict(cfg) if isinstance(cfg, PipelineConfig) else cfg
