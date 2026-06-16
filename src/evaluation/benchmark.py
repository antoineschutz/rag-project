"""Quantitative benchmark: keyword-scored accuracy over the QA pairs.

Runs a config over the question set, reusing the shared LLM answer cache so a config
whose answers are already cached scores instantly without touching Ollama. Each answer
is scored by case-insensitive AND-substring matching against the question's `keywords`;
the 29 questions with non-empty keywords give the headline `accuracy_29`. An independent
LLM-as-judge (a separate API model) gives a second opinion, and each run is tracked in
MLflow.
"""

import time
from typing import Any

import mlflow

from src.config import PipelineConfig, as_config_dict, env
from src.config.params import IndexParams
from src.evaluation import ANSWER_CACHE_PATH
from src.evaluation.qa_pairs import QA_PAIRS
from src.evaluation.runner import answer_for_config
from src.evaluation.scoring import judge_answer, score_answer
from src.llm.client import LLMClient
from src.utils.answer_cache import AnswerCache

EXPERIMENT_NAME = "rag-benchmark"
# LLM-as-judge: an independent API model (NOT the local LLM under test).
JUDGE_BACKEND = "gpt"
JUDGE_MODEL = "gpt-4o-mini"


def _on_event(event: str, qa: dict[str, Any], index_params: IndexParams | None) -> None:
    """Print progress for the shared answer loop (cached questions stay silent)."""
    if event == "build" and index_params is not None:
        print(f"  building index ({index_params.embed_model})...", flush=True)
    elif event == "generate":
        print(f"  Q{qa['id']} (level {qa['level']})...", flush=True)


def run_benchmark(
    config_name: str, cfg: PipelineConfig | dict[str, Any], fresh: bool = False,
    judge: bool = False, use_source: bool = False,
) -> dict[str, Any]:
    """Run one config over the keyword-scored questions and return results + accuracy_29.

    Answers come from the shared LLM cache unless `fresh` is set, which regenerates
    every answer (and refreshes the cache). Latency is only measured for a fresh
    run; a cached run's timing is meaningless, so `latency_s` is None otherwise.

    If `judge` is set, an independent API model (not the local LLM) also grades each
    answer against the reference; `score_judge` and the keyword/judge disagreement
    count are returned alongside the keyword `accuracy_29`.

    If `use_source` is set, each question is retrieved with its labeled source as a filter
    (the oracle source-filter experiment); these answers cache separately from the unfiltered run.
    """
    cfg = as_config_dict(cfg)  # accept a PipelineConfig (preset) or an inline dict
    scored = [qa for qa in QA_PAIRS if qa["keywords"]]
    cache = AnswerCache(ANSWER_CACHE_PATH)
    judge_client = LLMClient(backend=JUDGE_BACKEND, model=JUDGE_MODEL) if judge else None

    t0 = time.time()
    answers = answer_for_config(scored, cfg, cache, fresh=fresh, use_source=use_source, on_event=_on_event)

    results: list[dict[str, Any]] = []
    correct = 0
    judge_correct = 0
    disagreements = 0

    for qa, answer in zip(scored, answers):
        ok = score_answer(answer, qa["keywords"])
        correct += int(ok)

        judged: bool | None = None
        if judge_client is not None:
            judged = judge_answer(qa["question"], qa["expected"], answer, judge_client)
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
        "use_source": use_source,
        "latency_s": (time.time() - t0) if fresh else None,
        "judge": judge,
        "score_judge": (judge_correct / len(scored)) if (judge and scored) else None,
        "judge_disagreements": disagreements if judge else None,
    }


def log_to_mlflow(report: dict[str, Any]) -> None:
    """Log one benchmark run to MLflow: config as params, scores as metrics, full results as an artifact."""
    mlflow.set_experiment(EXPERIMENT_NAME)
    run_name = report["config_name"] + ("+src" if report.get("use_source") else "")
    with mlflow.start_run(run_name=run_name):
        mlflow.log_param("config_name", report["config_name"])
        mlflow.log_param("fresh", report["fresh"])
        mlflow.log_param("use_source", report.get("use_source", False))
        mlflow.log_param("judge", report["judge"])
        if report["judge"]:
            mlflow.log_param("judge_model", JUDGE_MODEL)
        mlflow.log_params(report["config"])
        if "num_ctx" not in report["config"]:
            mlflow.log_param("num_ctx", env.OLLAMA_NUM_CTX)
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
