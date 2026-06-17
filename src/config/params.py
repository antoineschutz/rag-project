"""Parameter groups for the pipeline, split by lifetime.

Three dataclasses capture the full knob set, grouped by when they matter:

- IndexParams: everything that determines the built index. Changing any field means
  the index (chunks + embeddings + retriever) must be rebuilt, so these are the sole
  basis for the on-disk cache identity.
- RetrievalParams: per-query knobs applied against an already-built index.
- GenerationParams: LLM knobs for the answer step.

The CLI (argparse), the API (QueryRequest), and the PRESETS map onto these groups.
`from_dict` builds a group from a flat kwargs dict, ignoring keys
that belong to the other groups, so one flat config can feed all three. Defaults are drawn
from BASE / env so there is one place to change them.
"""

from dataclasses import asdict, dataclass, fields
from typing import Any

# Import the sibling modules directly (not the package root) to avoid partial-init order issues.
from src.config.env import env
from src.config.pipeline import BASE


def _pick(cls: type, d: dict[str, Any]) -> dict[str, Any]:
    """Return the subset of d whose keys are fields of the dataclass cls."""
    names = {f.name for f in fields(cls)}
    return {k: v for k, v in d.items() if k in names}


@dataclass(frozen=True)
class IndexParams:
    """Index-defining params. Changing any field requires a rebuild (cache key basis)."""

    data_path: str = env.DATA_PATH
    retriever: str = BASE.retriever  # dense | bm25 | hybrid
    embed_model: str = BASE.embed_model
    store: str = BASE.store  # numpy | faiss | qdrant
    index_type: str = BASE.index_type  # flat | ivf
    chunk_max_tokens: int = BASE.chunk_max_tokens
    chunk_overlap: int = BASE.chunk_overlap  # present for completeness, not yet wired

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "IndexParams":
        return cls(**_pick(cls, d))

    def to_kwargs(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RetrievalParams:
    """Per-query retrieval knobs applied against an already-built index."""

    query: str
    top_k: int = BASE.top_k
    rerank: bool = BASE.rerank
    hyde: bool = BASE.hyde
    fusion: str = BASE.fusion  # rrf | weighted (hybrid only)
    alpha: float = BASE.alpha  # dense weight for weighted fusion (hybrid only)
    # Restrict retrieval to these document sources (filenames); None = all sources.
    source: str | list[str] | None = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "RetrievalParams":
        return cls(**_pick(cls, d))

    def to_kwargs(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GenerationParams:
    """LLM knobs for the answer step. no_rag decides whether retrieval happens at all.

    backend/model/num_ctx default to None so LLMClient can resolve them from the environment
    per backend (env.LLM_BACKEND / OLLAMA_MODEL / OPENAI_MODEL / OLLAMA_NUM_CTX); no_rag is a
    per-request mode flag. Defaults still come from BASE so all three groups stay uniform.
    """

    no_rag: bool = BASE.no_rag
    backend: str | None = BASE.backend
    model: str | None = BASE.model
    num_ctx: int | None = BASE.num_ctx

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "GenerationParams":
        return cls(**_pick(cls, d))

    def to_kwargs(self) -> dict[str, Any]:
        return asdict(self)


def split_config(
    cfg: dict[str, Any], query: str
) -> tuple[IndexParams, RetrievalParams, GenerationParams]:
    """Split a flat config dict into the three param groups (index, retrieval, generation).

    Drops None so each group falls back to its own defaults, and injects the query that
    RetrievalParams requires. The same flat dict feeds all three; each from_dict picks only
    its own fields. This is the one place the CLI, the API, and the eval scripts build their
    param groups from a flat config.
    """
    flat = {k: v for k, v in cfg.items() if v is not None}
    flat["query"] = query
    return (
        IndexParams.from_dict(flat),
        RetrievalParams.from_dict(flat),
        GenerationParams.from_dict(flat),
    )
