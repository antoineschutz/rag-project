#!/usr/bin/env python3
"""CLI for the keyword-scored benchmark (see src/evaluation/benchmark.py for the logic).

Usage:
    python scripts/benchmark.py --config best
    python scripts/benchmark.py --config baseline
"""

import argparse
import sys
from pathlib import Path
from typing import Any

# Allow imports from project root.
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import PRESETS as CONFIGS
from src.evaluation.benchmark import (
    EXPERIMENT_NAME,
    JUDGE_MODEL,
    log_to_mlflow,
    run_benchmark,
)


def _print_report(report: dict[str, Any], verbose: bool = False) -> None:
    """Print per-question pass/fail and the accuracy summary.

    When verbose, also print the question, expected answer, matched keywords,
    and the model's full answer for each question.
    """
    src_tag = " +src" if report.get("use_source") else ""
    print(f"\n=== benchmark: {report['config_name']}{src_tag} ===")
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
    parser.add_argument("--use-source", action="store_true", dest="use_source",
                        help="Filter retrieval to each question's labeled source (oracle source-filter experiment)")
    args = parser.parse_args()

    report = run_benchmark(args.config, CONFIGS[args.config], fresh=args.fresh, judge=args.judge, use_source=args.use_source)
    _print_report(report, verbose=args.verbose)
    if not args.no_mlflow:
        log_to_mlflow(report)
        print(f"\nlogged to MLflow experiment '{EXPERIMENT_NAME}' (run `mlflow ui` to view)")


if __name__ == "__main__":
    main()
