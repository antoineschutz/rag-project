"""Synthetic scaling benchmark for the dense backends.

Sweeps numpy cosine, FAISS flat, FAISS IVF, and Qdrant over N random vectors and measures
index build time, memory, query latency (p50/p95), and recall@k vs exact brute force. The
retrievers are constructed directly from a raw embeddings matrix (not via build_index, which
is bound to the on-disk corpus) so N can be set freely. See scripts/benchmark_scale.py for the
CLI that runs each (backend, N) cell in its own subprocess.

The qdrant backend requires a running Qdrant server (QDRANT_URL): only the server uses the HNSW
engine, while the in-process ':memory:' client does brute-force search and would not measure
Qdrant's scaling. Qdrant memory lives in that server process, so it is not captured here.
"""

import json
import logging
import os
import time
from typing import Any, Callable

import numpy as np

logger = logging.getLogger(__name__)

EXPERIMENT_NAME = "rag-scale"
BACKENDS = ("numpy", "faiss-flat", "faiss-ivf", "qdrant")
SCALE_COLLECTION = "scale_bench"  # recreated each qdrant cell (RetrieverQdrant drops + recreates)


def _make_vectors(n: int, dim: int, seed: int) -> np.ndarray:
    """Return n L2-normalized random float32 vectors (so inner product equals cosine)."""
    rng = np.random.default_rng(seed)
    vecs = rng.standard_normal((n, dim)).astype("float32")
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return vecs / norms


def _make_docs(n: int) -> list[dict[str, str]]:
    """Synthetic docs whose text is the vector id, so a retriever's returned text recovers it."""
    return [{"text": str(i), "source": "synthetic"} for i in range(n)]


def _resolve_backend(backend: str) -> Callable[[np.ndarray, list[dict[str, str]]], Any]:
    """Import the backend's deps and return a constructor closure.

    Importing here (before the memory baseline is sampled in measure_cell) keeps the library
    import cost out of the measured index footprint.
    """
    if backend == "numpy":
        from src.retrieval.retriever_cosine import RetrieverCosine
        return lambda emb, docs: RetrieverCosine(docs, emb)
    if backend == "faiss-flat":
        from src.retrieval.retriever_faiss import RetrieverFAISS
        return lambda emb, docs: RetrieverFAISS(docs, emb, index_type="flat")
    if backend == "faiss-ivf":
        from src.retrieval.retriever_faiss import RetrieverFAISS
        return lambda emb, docs: RetrieverFAISS(docs, emb, index_type="ivf")
    if backend == "qdrant":
        from qdrant_client import QdrantClient
        from src.retrieval.retriever_qdrant import RetrieverQdrant
        url = os.environ.get("QDRANT_URL")
        if not url:
            raise RuntimeError(
                "The qdrant backend needs a running Qdrant server (set QDRANT_URL, e.g. "
                "http://localhost:6333; start one with "
                "`docker compose -f docker/docker-compose.yml up -d qdrant`). The in-process "
                "':memory:' client does brute-force search, not HNSW, so it does not measure "
                "Qdrant's actual scaling."
            )
        client = QdrantClient(url=url, timeout=600)  # large N: upsert/index can exceed the default
        return lambda emb, docs: RetrieverQdrant(docs, emb, client=client, collection=SCALE_COLLECTION)
    raise ValueError(f"unknown backend: {backend!r} (expected one of {BACKENDS})")


def _wait_qdrant_indexed(client: Any, collection: str, n: int, timeout_s: float = 600.0) -> None:
    """Force HNSW indexing of every vector and block until it finishes.

    Qdrant only HNSW-indexes a segment once it exceeds the optimizer's indexing_threshold (default
    20000) and builds the index in the background, so queries issued right after upsert can hit
    unindexed (brute-force) segments. Lowering the threshold and waiting until indexed_vectors_count
    reaches n makes the latency/recall numbers reflect the real index.
    """
    from qdrant_client.models import OptimizersConfigDiff

    client.update_collection(
        collection_name=collection,
        optimizers_config=OptimizersConfigDiff(indexing_threshold=1),
    )
    deadline = time.perf_counter() + timeout_s
    while time.perf_counter() < deadline:
        if (client.get_collection(collection).indexed_vectors_count or 0) >= n:
            return
        time.sleep(0.5)
    logger.warning("qdrant indexing did not reach %d vectors within %.0fs", n, timeout_s)


def build_retriever(backend: str, embeddings: np.ndarray, docs: list[dict[str, str]]) -> Any:
    """Construct one backend's retriever directly from a raw embeddings matrix."""
    return _resolve_backend(backend)(embeddings, docs)


def _exact_topk(embeddings: np.ndarray, query_vecs: np.ndarray, top_k: int) -> list[set[int]]:
    """Brute-force exact top-k ids per query (both inputs normalized, so dot == cosine)."""
    sims = query_vecs @ embeddings.T
    k = min(top_k, embeddings.shape[0])
    part = np.argpartition(-sims, k - 1, axis=1)[:, :k]
    return [set(row.tolist()) for row in part]


def measure_cell(
    backend: str, n: int, dim: int, queries: int, top_k: int, seed: int
) -> dict[str, Any]:
    """Build one backend over N synthetic vectors and measure build/memory/latency/recall."""
    import psutil

    make = _resolve_backend(backend)  # import deps before the memory baseline
    proc = psutil.Process()

    rss_baseline = proc.memory_info().rss
    embeddings = _make_vectors(n, dim, seed)
    docs = _make_docs(n)
    query_vecs = _make_vectors(queries, dim, seed + 1)

    t0 = time.perf_counter()
    retriever = make(embeddings, docs)
    if backend == "qdrant":
        _wait_qdrant_indexed(retriever.client, retriever.collection, n)
    build_time_s = time.perf_counter() - t0
    # Qdrant runs in a separate server process, so client-side RSS is not its footprint.
    mem_rss_mb = None if backend == "qdrant" else max(0.0, (proc.memory_info().rss - rss_baseline) / 1e6)

    exact = _exact_topk(embeddings, query_vecs, top_k)

    for qi in range(min(3, queries)):  # warm up before timing
        retriever._retrieve_vec(query_vecs[qi : qi + 1], top_k=top_k)

    latencies = []
    recalls = []
    for qi in range(queries):
        q = query_vecs[qi : qi + 1]
        t = time.perf_counter()
        results = retriever._retrieve_vec(q, top_k=top_k)
        latencies.append((time.perf_counter() - t) * 1000.0)
        got = {int(r["text"]) for r in results}
        recalls.append(len(got & exact[qi]) / min(top_k, n))

    lat = np.array(latencies)
    nprobe = int(retriever.index.nprobe) if backend == "faiss-ivf" else None
    return {
        "backend": backend,
        "n": n,
        "dim": dim,
        "top_k": top_k,
        "queries": queries,
        "seed": seed,
        "nprobe": nprobe,
        "build_time_s": build_time_s,
        "mem_rss_mb": mem_rss_mb,
        "latency_p50_ms": float(np.percentile(lat, 50)),
        "latency_p95_ms": float(np.percentile(lat, 95)),
        "recall_at_k": float(np.mean(recalls)),
    }


def log_scale_run(cell: dict[str, Any]) -> None:
    """Log one measured cell to the 'rag-scale' MLflow experiment (separate from rag-benchmark)."""
    import mlflow

    from src.config import env

    mlflow.set_tracking_uri(env.MLFLOW_TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)
    with mlflow.start_run(run_name=f"{cell['backend']}-N{cell['n']}"):
        for k in ("backend", "n", "dim", "top_k", "queries", "seed", "nprobe"):
            mlflow.log_param(k, cell[k])
        for k in ("build_time_s", "mem_rss_mb", "latency_p50_ms", "latency_p95_ms", "recall_at_k"):
            if cell[k] is not None:  # qdrant memory is server-side, not measured here
                mlflow.log_metric(k, cell[k])


def make_chart(rows: list[dict[str, Any]], out_dir: str) -> str:
    """Render the 2x2 scaling chart and dump the raw rows. Returns the PNG path."""
    import os

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(out_dir, exist_ok=True)
    backends = sorted({r["backend"] for r in rows})
    # Recall is measured and logged but intentionally not charted: on random vectors it reflects
    # exact-rank reproduction on adversarial data, not retrieval quality (that is the BEIR job).
    panels = [
        ("latency_p50_ms", "query latency p50 (ms)", True),
        ("latency_p95_ms", "query latency p95 (ms)", True),
        ("mem_rss_mb", "memory (MB)", True),
        ("build_time_s", "index build time (s)", True),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    for ax, (metric, label, log_y) in zip(axes.flat, panels):
        for b in backends:
            pts = sorted(
                (r["n"], r[metric]) for r in rows if r["backend"] == b and r[metric] is not None
            )
            if pts:
                ax.plot([p[0] for p in pts], [p[1] for p in pts], marker="o", label=b)
        ax.set_xscale("log")
        if log_y:
            ax.set_yscale("log")
        ax.set_xlabel("N (vectors)")
        ax.set_title(label)
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(fontsize=8)
    fig.suptitle("Dense backend scaling (synthetic vectors)")
    fig.tight_layout()
    png = os.path.join(out_dir, "scale.png")
    fig.savefig(png, dpi=120)
    plt.close(fig)
    with open(os.path.join(out_dir, "scale_results.json"), "w") as f:
        json.dump(rows, f, indent=2)
    return png
