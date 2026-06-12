"""Markdown comparison report for an eval dimension.

Runs each config in a dimension over the question set (reusing the shared answer cache)
and writes one markdown file per dimension: a per-question table of answers side by side,
a config summary, and a runtime breakdown.
"""

import time
from pathlib import Path
from typing import Any

from src.config import as_config_dict, env
from src.config.params import IndexParams
from src.evaluation import ANSWER_CACHE_PATH
from src.evaluation.qa_pairs import QA_PAIRS
from src.evaluation.runner import answer_for_config
from src.utils.answer_cache import AnswerCache

OUT_DIR = Path("eval_results2")


def _cell(text: str) -> str:
    """Sanitize text for a markdown table cell."""
    return text.replace("|", "\\|").replace("\n", "<br>").strip()


def _config_summary(labels: list[str], configs: list[dict]) -> str:
    """Render a small config table for the top of the output file."""
    rows = ["| Parameter | " + " | ".join(labels) + " |"]
    rows.append("|-----------|" + "|".join(["--------"] * len(labels)) + "|")

    keys = ["retriever", "embed_model", "fusion", "alpha", "rerank", "top_k", "no_rag", "chunk_max_tokens"]
    for k in keys:
        values = [str(cfg.get(k, "—")) for cfg in configs]
        if len(set(values)) > 1 or any(v != "—" for v in values):
            rows.append(f"| {k} | " + " | ".join(values) + " |")
    return "\n".join(rows)


def _write_question(
    f: Any,
    qa: dict,
    labels: list[str],
    answers: list[str],
) -> None:
    """Append one question section to an open file handle."""
    f.write(f"\n## Q{qa['id']} · Level {qa['level']}\n\n")
    f.write(f"**Question:** {qa['question']}  \n")
    f.write(f"**Expected:** {qa['expected']}  \n")
    f.write(f"**Source:** `{qa['source']}`\n\n")

    header = "| " + " | ".join(labels) + " |"
    sep = "|" + "|".join(["---"] * len(labels)) + "|"
    row = "| " + " | ".join(_cell(a) for a in answers) + " |"
    f.write(header + "\n" + sep + "\n" + row + "\n")


def run_dimension(name: str, labels: list[str], configs: list[Any]) -> None:
    """Run every config in one dimension and write its markdown comparison file."""
    active = [qa for qa in QA_PAIRS if qa["question"]]
    if not active:
        print(f"[{name}] No questions filled in, skipping.")
        return

    # Flatten typed PipelineConfig presets to plain dicts for splitting / cache keys / summary.
    configs = [as_config_dict(c) for c in configs]

    print(f"\n=== {name} ({len(active)} questions × {len(configs)} configs) ===")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{name}.md"

    model = env.OLLAMA_MODEL if env.LLM_BACKEND == "ollama" else env.OPENAI_MODEL

    # answers_matrix[q_idx][cfg_idx]
    answers_matrix: list[list[str]] = [[""] * len(configs) for _ in active]
    cache = AnswerCache(ANSWER_CACHE_PATH)

    cfg_times: list[float] = []
    for i, cfg in enumerate(configs):
        cfg_t0 = time.time()

        def _on_event(event: str, qa: dict, index_params: IndexParams | None, label: str = labels[i]) -> None:
            """Print progress for one config column of the matrix."""
            if event == "cached":
                print(f"    Q{qa['id']} [{label}] (cached)", flush=True)
            elif event == "build":
                print(f"\n  [{label}] building index...", flush=True)
            elif event == "generate":
                print(f"    Q{qa['id']} (level {qa['level']}) [{label}]...", flush=True)

        answers = answer_for_config(active, cfg, cache, on_event=_on_event)
        for j, ans in enumerate(answers):
            answers_matrix[j][i] = ans

        cfg_elapsed = time.time() - cfg_t0
        cfg_times.append(cfg_elapsed)
        print(f"  [{labels[i]}] done in {cfg_elapsed:.0f}s", flush=True)

    with open(out_path, "w") as f:
        f.write(f"# {name}\n\n")
        f.write(f"**backend:** {env.LLM_BACKEND} · **model:** {model}\n\n")
        f.write(_config_summary(labels, configs))
        f.write("\n\n---\n")
        for j, qa in enumerate(active):
            _write_question(f, qa, labels, answers_matrix[j])
        f.write("\n\n---\n\n## Runtime\n\n")
        f.write("| Config | Time |\n|--------|------|\n")
        for label, t in zip(labels, cfg_times):
            f.write(f"| {label} | {t/60:.1f} min |\n")
        f.write(f"| **total** | **{sum(cfg_times)/60:.1f} min** |\n")

    print(f"  -> {out_path}")
