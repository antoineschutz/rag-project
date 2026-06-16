"""FastAPI server exposing the RAG pipeline over HTTP.

Run with:
    uvicorn src.api.server:app --reload

Endpoints: /health, /presets, /sources (document filenames for the source filter),
/query (answer + retrieved chunks), /evaluate (score a config over the QA set),
/compare (one query across two configs).
"""

import json
import logging
from collections.abc import Iterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from src.pipeline import answer_query, answer_query_stream
from src.config import PRESETS, IndexParams, as_config_dict, env, split_config
from src.api import state
from src.api.schemas import (
    CompareRequest,
    CompareResponse,
    CompareSide,
    EvaluateRequest,
    EvaluateResponse,
    QueryRequest,
    QueryResponse,
)

logger = logging.getLogger(__name__)


def _warmup() -> None:
    """Preload the embedder/index/reranker for env.WARMUP_PRESETS so the first real request
    is not cold. Non-fatal: a preset that fails to warm is logged and skipped (it will just
    build lazily on its first query). Set env.WARMUP_PRESETS = () to disable.
    """
    for name in env.WARMUP_PRESETS:
        if name not in PRESETS:
            logger.warning("warmup: unknown preset %r, skipping", name)
            continue
        cfg = as_config_dict(PRESETS[name])
        try:
            if not cfg.get("no_rag"):
                state.get_retriever(IndexParams.from_dict(cfg))
                if cfg.get("rerank"):
                    state.get_reranker()
            logger.info("warmup: %s ready", name)
        except Exception as exc:  # warmup must never crash startup
            logger.warning("warmup: %s failed (%s); will build lazily", name, exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Warm the configured presets before the server starts accepting requests."""
    _warmup()
    yield


app = FastAPI(
    title="RAG pipeline API",
    description="HTTP interface to a from-scratch RAG pipeline (query, evaluate, compare).",
    version="0.1.0",
    lifespan=lifespan,
)


def _build_pipeline(query_text: str, cfg: dict[str, Any]):
    """Resolve cfg into (retriever, rp, gp, reranker), reusing the memoized retriever/reranker.

    `cfg` is a (possibly sparse) flat config (a PRESETS entry or a QueryRequest dump). Dropping
    None lets each param group apply its own default. The retriever is fetched from the in-process
    cache (built once, reused across requests); this is the two-phase interface, so no per-call
    injection into the pipeline is needed.
    """
    index_params, rp, gp = split_config(cfg, query_text)
    retriever = None if gp.no_rag else state.get_retriever(index_params)
    reranker = state.get_reranker() if (rp.rerank and not gp.no_rag) else None
    return retriever, rp, gp, reranker


def _run_with_state(
    query_text: str, cfg: dict[str, Any], history: list[dict[str, str]] | None = None
) -> dict[str, Any]:
    """Run one query (non-streaming) over the memoized retriever/reranker for this config."""
    retriever, rp, gp, reranker = _build_pipeline(query_text, cfg)
    return answer_query(retriever, rp, gp, reranker=reranker, history=history)


def _history(req: QueryRequest) -> list[dict[str, str]] | None:
    """Flatten the request's typed history turns into the plain dicts the pipeline expects."""
    return [t.model_dump() for t in req.history] if req.history else None


def _resolve_config(ref: str | dict[str, Any]) -> dict[str, Any]:
    """Turn a preset name or inline config into a config dict, 400 on an unknown name."""
    if isinstance(ref, str):
        if ref not in PRESETS:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown preset '{ref}'. Available: {sorted(PRESETS)}",
            )
        return as_config_dict(PRESETS[ref])
    return ref


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check: returns ok if the server is up."""
    return {"status": "ok"}


@app.get("/presets")
def presets() -> dict[str, dict[str, Any]]:
    """List the named presets (name -> config) so a client can offer them as choices."""
    return {name: as_config_dict(pc) for name, pc in PRESETS.items()}


@app.get("/sources")
def sources() -> list[str]:
    """List the document sources (filenames) in the data dir, for the source filter."""
    from pathlib import Path
    data_dir = Path(env.DATA_PATH)
    names = {
        p.name
        for ext in ("*.pdf", "*.md", "*.txt", "*.docx")
        for p in data_dir.glob(ext)
    }
    return sorted(names)


def _query_config(req: QueryRequest) -> dict[str, Any]:
    """Resolve QueryRequest.config: None -> best preset, str -> named preset, QueryConfig -> set knobs."""
    if req.config is None:
        return as_config_dict(PRESETS["best"])
    if isinstance(req.config, str):
        return _resolve_config(req.config)  # validates the preset name (400 if unknown)
    return req.config.model_dump(exclude_none=True)  # keep only the knobs the caller actually set


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest) -> QueryResponse:
    """Run one query and return the answer plus retrieved chunks.

    `config` selects the pipeline: omit it for the best preset, pass a preset name, or pass
    inline knob overrides (unspecified knobs fall back to the base config defaults).
    """
    cfg = _query_config(req)
    result = _run_with_state(req.query, cfg, _history(req))
    return QueryResponse(
        answer=result["answer"], chunks=result["chunks"], config=cfg,
        hyde_doc=result.get("hyde_doc"), standalone_query=result.get("standalone_query"),
    )


@app.post("/query/stream")
def query_stream(req: QueryRequest) -> StreamingResponse:
    """Run one query and stream the answer as newline-delimited JSON (NDJSON).

    Config selection is identical to /query; pass `history` for multi-turn chat. The first line is
    {"type": "meta", "chunks": [...], "config": {...}, "hyde_doc": ..., "standalone_query": ...},
    followed by one {"type": "token", "text": ...} per generated chunk. If generation fails
    mid-stream a final {"type": "error", "detail": ...} line is emitted.
    """
    cfg = _query_config(req)
    retriever, rp, gp, reranker = _build_pipeline(req.query, cfg)
    history = _history(req)

    def ndjson() -> Iterator[str]:
        try:
            for event in answer_query_stream(retriever, rp, gp, reranker=reranker, history=history):
                if event["type"] == "meta":
                    event = {**event, "config": cfg}
                yield json.dumps(event) + "\n"
        except Exception as exc:  # already-streaming: report via an error line, not a 500
            yield json.dumps({"type": "error", "detail": str(exc)}) + "\n"

    return StreamingResponse(ndjson(), media_type="application/x-ndjson")


@app.post("/evaluate", response_model=EvaluateResponse)
def evaluate(req: EvaluateRequest) -> EvaluateResponse:
    """Score a config over the keyword-graded QA set. Uses cached answers unless `fresh`.

    A known preset `name` wins: it is run and any inline `config` is ignored. Only when `name` is not a preset
    is the inline `config` used.
    """
    if req.name in PRESETS:
        cfg = PRESETS[req.name]
        label = req.name
    elif req.config is not None:
        cfg = req.config
        label = req.name or "custom"
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown preset '{req.name}'. Available: {sorted(PRESETS)}",
        )

    # run_benchmark pulls in mlflow; import it lazily so the server starts without paying that cost.
    from src.evaluation.benchmark import run_benchmark

    report = run_benchmark(label, cfg, fresh=req.fresh, judge=req.judge)
    return EvaluateResponse(**report)


@app.post("/compare", response_model=CompareResponse)
def compare(req: CompareRequest) -> CompareResponse:
    """Run one query through two configs and return both answers and chunks side by side."""
    cfg_a = _resolve_config(req.a)
    cfg_b = _resolve_config(req.b)
    res_a = _run_with_state(req.query, cfg_a)
    res_b = _run_with_state(req.query, cfg_b)
    return CompareResponse(
        query=req.query,
        a=CompareSide(config=cfg_a, answer=res_a["answer"], chunks=res_a["chunks"]),
        b=CompareSide(config=cfg_b, answer=res_b["answer"], chunks=res_b["chunks"]),
    )
