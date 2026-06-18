"""BEIR retrieval-quality benchmark.

Evaluates BM25 / dense / hybrid / +rerank on BEIR datasets (SciFact, NFCorpus) with standard IR
metrics (nDCG@k, Recall@k, MRR via pytrec_eval). Retrieval-only: it scores the ranked document
list against the dataset's relevance judgments, with no LLM. Datasets download to var/beir/ and
each document is embedded whole (BEIR convention, no chunking). See scripts/benchmark_beir.py.

pytrec_eval is an eval-only dependency (requirements-eval.txt), not needed to run the app.
"""

import csv
import json
import logging
import os
import time
import urllib.request
import zipfile
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

EXPERIMENT_NAME = "rag-beir"
BEIR_URL = "https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/{name}.zip"
DATASETS = ("scifact", "nfcorpus")
CONFIGS = ("bm25", "dense-minilm", "dense-bge", "hybrid", "hybrid-rerank")
K_VALUES = (1, 3, 5, 10)
_MODELS = {"minilm": "all-MiniLM-L6-v2", "bge": "BAAI/bge-small-en-v1.5"}


def download_dataset(dataset_name: str, out_dir: str = "var/beir") -> str:
    """Download and unzip a BEIR dataset into out_dir/dataset_name (cached). Returns the dataset dir."""
    dpath = os.path.join(out_dir, dataset_name)
    if os.path.exists(os.path.join(dpath, "corpus.jsonl")):
        return dpath
    os.makedirs(out_dir, exist_ok=True)
    zpath = os.path.join(out_dir, f"{dataset_name}.zip")
    logger.info("downloading BEIR/%s ...", dataset_name)
    urllib.request.urlretrieve(BEIR_URL.format(name=dataset_name), zpath)
    with zipfile.ZipFile(zpath) as archive:
        archive.extractall(out_dir)
    os.remove(zpath)
    return dpath


def load_dataset(
    dataset_name: str, out_dir: str = "var/beir", split: str = "test"
) -> tuple[dict[str, str], dict[str, str], dict[str, dict[str, int]]]:
    """Return (corpus, queries, qrels): corpus doc_id->text, queries qid->text, qrels qid->{doc_id:rel}."""
    dataset_dir = download_dataset(dataset_name, out_dir)
    corpus = {}
    with open(os.path.join(dataset_dir, "corpus.jsonl")) as f:
        for line in f:
            record = json.loads(line)
            corpus[record["_id"]] = (record.get("title", "") + " " + record.get("text", "")).strip()
    queries = {}
    with open(os.path.join(dataset_dir, "queries.jsonl")) as f:
        for line in f:
            record = json.loads(line)
            queries[record["_id"]] = record["text"]
    qrels: dict[str, dict[str, int]] = {}
    with open(os.path.join(dataset_dir, "qrels", f"{split}.tsv")) as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)  # header: query-id, corpus-id, score
        for qid, did, score in reader:
            qrels.setdefault(qid, {})[did] = int(score)
    # queries.jsonl holds all splits; keep only the ones judged in this split's qrels
    queries = {qid: q for qid, q in queries.items() if qid in qrels}
    return corpus, queries, qrels


def _embed_corpus(
    texts: list[str], model_name: str, dataset_name: str, out_dir: str, device: str | None
) -> tuple[np.ndarray, Any]:
    """Embed the corpus with model_name (cached to out_dir); return (embeddings, embedder)."""
    from src.embeddings.embed import Embedder

    embedder = Embedder(model_name=model_name, device=device)
    cache = os.path.join(out_dir, f"emb_{dataset_name}_{model_name.replace('/', '_')}.npy")
    if os.path.exists(cache):
        return np.load(cache), embedder
    emb = embedder.embed_documents(texts)
    np.save(cache, emb)
    return emb, embedder


def build_beir_retriever(
    config: str, corpus: dict[str, str], dataset_name: str, out_dir: str, device: str | None = "cpu"
) -> tuple[Any, Any]:
    """Construct the retriever (and optional reranker) for a config from the BEIR corpus.

    Each doc becomes one entry {text, source=doc_id} so retrieve() results carry the doc_id.
    Models default to CPU: the cross-encoder reranker exhausts Apple MPS memory on a small
    machine, and the corpora are tiny so CPU is fast enough.
    """
    from src.retrieval.retriever_bm25 import RetrieverBM25

    doc_ids = list(corpus)
    texts = [corpus[doc_id] for doc_id in doc_ids]
    docs = [{"text": texts[i], "source": doc_ids[i]} for i in range(len(doc_ids))]

    if config == "bm25":
        return RetrieverBM25(docs), None

    from src.retrieval.retriever_cosine import RetrieverCosine

    model = _MODELS["bge"] if config == "dense-bge" else _MODELS["minilm"]
    emb, embedder = _embed_corpus(texts, model, dataset_name, out_dir, device)
    dense = RetrieverCosine(docs, emb, embedder=embedder)
    if config in ("dense-minilm", "dense-bge"):
        return dense, None

    from src.retrieval.retriever_hybrid import RetrieverHybrid

    hybrid = RetrieverHybrid(dense, RetrieverBM25(docs), fusion="rrf")
    if config == "hybrid":
        return hybrid, None

    from src.reranker.reranker import Reranker  # config == "hybrid-rerank"

    return hybrid, Reranker(device=device)


def retrieve_all(
    retriever: Any, queries: dict[str, str], top_k: int, reranker: Any = None
) -> dict[str, dict[str, float]]:
    """Run every query, returning the TREC-style run {qid: {doc_id: score}}."""
    run: dict[str, dict[str, float]] = {}
    for qid, qtext in queries.items():
        results = retriever.retrieve(qtext, top_k=top_k)
        if reranker is not None:
            results = reranker.rerank(qtext, results, top_k=top_k)
        run[qid] = {r["source"]: float(r["score"]) for r in results}
    return run


def evaluate(
    qrels: dict[str, dict[str, int]], run: dict[str, dict[str, float]], k_values: tuple[int, ...] = K_VALUES
) -> dict[str, float]:
    """Compute nDCG@k, Recall@100, MRR, and MAP with pytrec_eval, averaged over queries."""
    import pytrec_eval

    ndcg = "ndcg_cut." + ",".join(str(k) for k in k_values)
    evaluator = pytrec_eval.RelevanceEvaluator(qrels, {ndcg, "recall.100", "recip_rank", "map"})
    per_query = evaluator.evaluate(run)
    n_queries = len(per_query) or 1

    def mean(key: str) -> float:
        return sum(scores[key] for scores in per_query.values()) / n_queries

    metrics = {f"ndcg@{k}": mean(f"ndcg_cut_{k}") for k in k_values}
    metrics["recall@100"] = mean("recall_100")
    metrics["mrr"] = mean("recip_rank")
    metrics["map"] = mean("map")
    return metrics


def run_beir(
    dataset_name: str, config: str, top_k: int = 100, out_dir: str = "var/beir",
    k_values: tuple[int, ...] = K_VALUES, device: str | None = "cpu",
) -> dict[str, Any]:
    """Load a dataset, build the config's retriever, retrieve, and score. Returns a report dict."""
    corpus, queries, qrels = load_dataset(dataset_name, out_dir)
    t0 = time.perf_counter()
    retriever, reranker = build_beir_retriever(config, corpus, dataset_name, out_dir, device)
    run = retrieve_all(retriever, queries, top_k, reranker)
    metrics = evaluate(qrels, run, k_values)
    return {
        "dataset": dataset_name, "config": config, "top_k": top_k,
        "n_queries": len(queries), "n_docs": len(corpus),
        "elapsed_s": time.perf_counter() - t0, **metrics,
    }


def log_beir_run(report: dict[str, Any]) -> None:
    """Log one BEIR report to the 'rag-beir' MLflow experiment (separate from rag-benchmark/rag-scale)."""
    import mlflow

    from src.config import env

    mlflow.set_tracking_uri(env.MLFLOW_TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)
    with mlflow.start_run(run_name=f"{report['dataset']}-{report['config']}"):
        for k in ("dataset", "config", "top_k", "n_queries", "n_docs"):
            mlflow.log_param(k, report[k])
        for k, v in report.items():
            if k.startswith(("ndcg@", "recall@")) or k in ("mrr", "map", "elapsed_s"):
                mlflow.log_metric(k.replace("@", "_at_"), v)
