#!/usr/bin/env python3
"""Quantitative benchmark: keyword-scored accuracy over the QA pairs.

Shares the question set and pipeline runner with the qualitative tool
(`scripts/eval.py`): it imports `QA_PAIRS` and the LLM-answer cache helpers from
there and `run_pipeline` from `main`, so a config whose answers are already
cached scores instantly without touching Ollama.

Each answer is scored by case-insensitive AND-substring matching against the
question's `keywords` (see eval.py for the field's semantics). Questions with
empty keywords are prose-only and excluded, leaving 29 scored questions, so the
headline metric is `accuracy_29`.

MLflow tracking and the LLM-as-judge safeguard are added in later steps.

Usage:
    python scripts/benchmark.py --config best
    python scripts/benchmark.py --config baseline
"""

import argparse
import sys
import time
from pathlib import Path
from typing import Any

import mlflow

# Allow imports from project root (mirrors eval.py).
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import config
from src.embeddings.embed import Embedder
from src.llm.client import LLMClient
from main import run_pipeline
from eval import QA_PAIRS, _cache_key, _load_cache, _save_cache

EXPERIMENT_NAME = "rag-benchmark"
# LLM-as-judge: an independent API model (NOT the local LLM under test).
JUDGE_BACKEND = "gpt"
JUDGE_MODEL = "gpt-4o-mini"


# ---------------------------------------------------------------------------
# Named configs to benchmark. Keys/values must match the corresponding eval.py
# config dicts exactly so their cached answers are reused.
# ---------------------------------------------------------------------------
CONFIGS: dict[str, dict[str, Any]] = {
    "no-rag": {"no_rag": True},
    "baseline": {
        "no_rag": False, "retriever": "dense",
        "embed_model": "all-MiniLM-L6-v2", "rerank": False, "top_k": 15,
    },
    "best": {
        "no_rag": False, "retriever": "hybrid", "fusion": "rrf", "alpha": 0.5,
        "embed_model": "BAAI/bge-small-en-v1.5", "rerank": True, "top_k": 20,
        "chunk_max_tokens": 128,
    },
    # best, but retrieve+rerank 40 chunks instead of 20. ~40×128 ≈ 5k context tokens,
    # which overflows the default 4096 window, so this config carries num_ctx=8192.
    "best-k40": {
        "no_rag": False, "retriever": "hybrid", "fusion": "rrf", "alpha": 0.5,
        "embed_model": "BAAI/bge-small-en-v1.5", "rerank": True, "top_k": 40,
        "chunk_max_tokens": 128, "num_ctx": 8192,
    },
    # best-k40 with larger 256-token chunks. ~40×256 ≈ 10k context tokens → num_ctx=16384.
    "best-k40-c256": {
        "no_rag": False, "retriever": "hybrid", "fusion": "rrf", "alpha": 0.5,
        "embed_model": "BAAI/bge-small-en-v1.5", "rerank": True, "top_k": 40,
        "chunk_max_tokens": 256, "num_ctx": 16384,
    },
}


def _score_answer(answer: str, keywords: list[str]) -> bool:
    """True if every keyword appears (case-insensitively) as a substring of answer."""
    haystack = answer.lower()
    return all(kw.lower() in haystack for kw in keywords)


def _judge_answer(question: str, expected: str, answer: str, client: LLMClient) -> bool:
    """Ask the judge LLM whether `answer` conveys the key fact(s) of `expected`."""
    prompt = (
        "You are grading a short factual answer against a reference answer.\n\n"
        f"Question: {question}\n"
        f"Reference answer: {expected}\n"
        f"Candidate answer: {answer}\n\n"
        "Does the candidate state the key fact(s) of the reference answer correctly? "
        "Ignore style, extra detail, and hedging. Reply with a single word: YES or NO."
    )
    return client.generate(prompt).strip().upper().startswith("Y")


def run_benchmark(
    config_name: str, cfg: dict[str, Any], fresh: bool = False, judge: bool = False
) -> dict[str, Any]:
    """Run one config over the keyword-scored questions and return results + accuracy_29.

    Answers come from the shared LLM cache unless `fresh` is set, which regenerates
    every answer (and refreshes the cache). Latency is only measured for a fresh
    run; a cached run's timing is meaningless, so `latency_s` is None otherwise.

    If `judge` is set, an independent API model (not the local LLM) also grades each
    answer against the reference; `score_judge` and the keyword/judge disagreement
    count are returned alongside the keyword `accuracy_29`.
    """
    scored = [qa for qa in QA_PAIRS if qa["keywords"]]
    cache = _load_cache()
    needs_embedder = not cfg.get("no_rag") and cfg.get("retriever", "dense") != "bm25"
    embedder: Embedder | None = None
    judge_client = LLMClient(backend=JUDGE_BACKEND, model=JUDGE_MODEL) if judge else None

    results: list[dict[str, Any]] = []
    correct = 0
    judge_correct = 0
    disagreements = 0
    t0 = time.time()

    for qa in scored:
        key = _cache_key(qa["question"], cfg)
        if not fresh and key in cache:
            answer = cache[key]
        else:
            if embedder is None and needs_embedder:
                print(f"  loading embedder ({cfg.get('embed_model') or config.EMBED_MODEL})...", flush=True)
                embedder = Embedder(cfg.get("embed_model") or config.EMBED_MODEL)
            print(f"  Q{qa['id']} (level {qa['level']})...", flush=True)
            answer = run_pipeline(qa["question"], embedder=embedder, **cfg)
            cache[key] = answer
            _save_cache(cache)

        ok = _score_answer(answer, qa["keywords"])
        correct += int(ok)

        judged: bool | None = None
        if judge_client is not None:
            judged = _judge_answer(qa["question"], qa["expected"], answer, judge_client)
            judge_correct += int(judged)
            if judged != ok:
                disagreements += 1

        results.append({
            "id": qa["id"], "level": qa["level"], "correct": ok, "judge": judged,
            "question": qa["question"], "expected": qa["expected"],
            "keywords": qa["keywords"], "answer": answer,
        })

    accuracy = correct / len(scored) if scored else 0.0
    return {
        "config_name": config_name,
        "config": cfg,
        "results": results,
        "n_scored": len(scored),
        "correct": correct,
        "accuracy_29": accuracy,
        "fresh": fresh,
        "latency_s": (time.time() - t0) if fresh else None,
        "judge": judge,
        "score_judge": (judge_correct / len(scored)) if (judge and scored) else None,
        "judge_disagreements": disagreements if judge else None,
    }


def _print_report(report: dict[str, Any], verbose: bool = False) -> None:
    """Print per-question pass/fail and the accuracy summary.

    When verbose, also print the question, expected answer, matched keywords,
    and the model's full answer for each question.
    """
    print(f"\n=== benchmark: {report['config_name']} ===")
    for r in report["results"]:
        mark = "✓" if r["correct"] else "✗"
        judged = r.get("judge")
        if judged is None:
            head = f"{mark} Q{r['id']:<2} (L{r['level']})"
        else:
            disagree = " ⚠" if judged != r["correct"] else ""
            head = f"kw {mark}  judge {'✓' if judged else '✗'}{disagree}  Q{r['id']:<2} (L{r['level']})"
        if verbose:
            print(f"\n  {head}  keywords: {r['keywords']}")
            print(f"      Q:        {r['question']}")
            print(f"      expected: {r['expected']}")
            print(f"      answer:   {r['answer']}")
        else:
            print(f"  {head}")
    summary = (
        f"\naccuracy_29 = {report['correct']}/{report['n_scored']} "
        f"= {report['accuracy_29']:.1%}"
    )
    summary += (
        f"   ({report['latency_s']:.0f}s)" if report["latency_s"] is not None
        else "   (cached, latency not measured)"
    )
    print(summary)
    if report.get("score_judge") is not None:
        print(
            f"score_judge = {report['score_judge']:.1%}   "
            f"(keyword/judge disagreements: {report['judge_disagreements']})"
        )


def _log_to_mlflow(report: dict[str, Any]) -> None:
    """Log one benchmark run to MLflow: config as params, scores as metrics, full results as an artifact."""
    mlflow.set_experiment(EXPERIMENT_NAME)
    with mlflow.start_run(run_name=report["config_name"]):
        mlflow.log_param("config_name", report["config_name"])
        mlflow.log_param("fresh", report["fresh"])
        mlflow.log_param("judge", report["judge"])
        if report["judge"]:
            mlflow.log_param("judge_model", JUDGE_MODEL)
        mlflow.log_params(report["config"])
        if "num_ctx" not in report["config"]:
            mlflow.log_param("num_ctx", config.OLLAMA_NUM_CTX)
        metrics = {
            "accuracy_29": report["accuracy_29"],
            "correct": report["correct"],
            "n_scored": report["n_scored"],
        }
        if report["latency_s"] is not None:
            metrics["latency_s"] = report["latency_s"]
        if report["score_judge"] is not None:
            metrics["score_judge"] = report["score_judge"]
            metrics["judge_disagreements"] = report["judge_disagreements"]
        mlflow.log_metrics(metrics)
        mlflow.log_dict(
            {"config": report["config"], "results": report["results"]},
            "results.json",
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Keyword-scored benchmark over the QA pairs.")
    parser.add_argument("--config", required=True, choices=list(CONFIGS.keys()),
                        help="Named config to benchmark")
    parser.add_argument("--verbose", action="store_true",
                        help="Print question, expected answer, and full model answer per question")
    parser.add_argument("--no-mlflow", action="store_true",
                        help="Skip MLflow logging (e.g. for quick local checks)")
    parser.add_argument("--fresh", action="store_true",
                        help="Bypass the answer cache and regenerate every answer; required for a real latency measurement")
    parser.add_argument("--judge", action="store_true",
                        help=f"Also grade each answer with an independent judge LLM ({JUDGE_MODEL}); needs OPENAI_API_KEY and makes ~29 API calls")
    args = parser.parse_args()

    report = run_benchmark(args.config, CONFIGS[args.config], fresh=args.fresh, judge=args.judge)
    _print_report(report, verbose=args.verbose)
    if not args.no_mlflow:
        _log_to_mlflow(report)
        print(f"\nlogged to MLflow experiment '{EXPERIMENT_NAME}' (run `mlflow ui` to view)")


if __name__ == "__main__":
    main()
