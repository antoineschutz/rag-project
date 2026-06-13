"""Pydantic request/response models for the API."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class QueryConfig(BaseModel):
    """Inline pipeline knobs for a manual /query.

    Every field is optional: only the ones provided are applied, the rest fall back to the
    base defaults in src/config (via the param-group defaults). Mirrors the knobs the API
    exposes (data_path / index_type / chunk_overlap are intentionally not exposed).
    """

    retriever: str | None = Field(None, description="dense, bm25, or hybrid.")
    top_k: int | None = Field(None, description="Number of chunks to feed the LLM.")
    rerank: bool | None = Field(None, description="Cross-encoder re-rank the retrieved chunks.")
    embed_model: str | None = Field(None, description="Sentence-transformers model.")
    chunk_max_tokens: int | None = Field(None, description="Max tokens per chunk.")
    num_ctx: int | None = Field(None, description="Ollama context window; None uses the config default.")
    no_rag: bool | None = Field(None, description="Skip retrieval and answer from the model alone.")
    fusion: str | None = Field(None, description="Hybrid fusion: rrf or weighted.")
    alpha: float | None = Field(None, description="Dense weight for weighted fusion.")
    hyde: bool | None = Field(None, description="Embed a hypothetical answer passage instead of the raw query.")
    store: str | None = Field(None, description="Dense backend store: numpy or faiss.")
    backend: str | None = Field(None, description="LLM backend: ollama or gpt; None uses the config default.")
    model: str | None = Field(None, description="LLM model name override.")


class Turn(BaseModel):
    """One prior conversation turn (client-managed history)."""

    role: Literal["user", "assistant"]
    content: str


class QueryRequest(BaseModel):
    query: str = Field(..., description="The question to answer.")
    config: str | QueryConfig | None = Field(
        None,
        description="A preset name (e.g. 'baseline'), inline knob overrides, or omitted to run the best preset.",
    )
    history: list[Turn] | None = Field(
        None,
        description="Prior turns for multi-turn chat. When given, the question is condensed into a "
        "standalone query before retrieval. Omit for a single-shot query.",
    )


class ChunkOut(BaseModel):
    text: str
    source: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    chunks: list[ChunkOut]
    config: dict[str, Any]
    hyde_doc: str | None = None  # the generated hypothetical passage when HyDE ran, else None
    standalone_query: str | None = None  # the condensed follow-up when history changed it, else None


class EvaluateRequest(BaseModel):
    name: str = Field("best", description="Preset name from src/config; a known preset wins and `config` is ignored.")
    config: dict[str, Any] | None = Field(
        None, description="Inline pipeline config; used only when `name` is not a known preset."
    )
    fresh: bool = Field(False, description="Bypass the answer cache and regenerate (needed for real latency).")
    judge: bool = Field(False, description="Also grade with the LLM judge; needs OPENAI_API_KEY and ~29 API calls.")


class EvaluateResponse(BaseModel):
    config_name: str
    config: dict[str, Any]
    n_scored: int
    correct: int
    accuracy_29: float
    fresh: bool
    latency_s: float | None
    judge: bool
    score_judge: float | None
    judge_disagreements: int | None
    results: list[dict[str, Any]]


class CompareRequest(BaseModel):
    query: str = Field(..., description="The question to run through both configs.")
    a: str | dict[str, Any] = Field("baseline", description="Preset name or inline config for side A.")
    b: str | dict[str, Any] = Field("best", description="Preset name or inline config for side B.")


class CompareSide(BaseModel):
    config: dict[str, Any]
    answer: str
    chunks: list[ChunkOut]


class CompareResponse(BaseModel):
    query: str
    a: CompareSide
    b: CompareSide
