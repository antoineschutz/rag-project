#!/usr/bin/env python3
"""CLI for the BEIR retrieval-quality benchmark (logic in src/evaluation/beir.py).

Evaluates the project's retrievers (BM25 / dense / hybrid / +rerank) on BEIR datasets with
nDCG@k, Recall@100, MRR, and MAP. Needs the eval-only dependency: pip install -r requirements-eval.txt

Usage:
    python scripts/benchmark_beir.py
    python scripts/benchmark_beir.py --datasets scifact --configs bm25 dense-minilm --no-mlflow
"""

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation.beir import CONFIGS, DATASETS, EXPERIMENT_NAME, log_beir_run, run_beir


def main() -> None:
    p = argparse.ArgumentParser(description="BEIR retrieval-quality benchmark for the dense/sparse stack.")
    p.add_argument("--datasets", nargs="+", default=list(DATASETS), choices=list(DATASETS))
    p.add_argument("--configs", nargs="+", default=list(CONFIGS), choices=list(CONFIGS))
    p.add_argument("--top-k", type=int, default=100, help="Candidates retrieved (and reranked) per query")
    p.add_argument("--out", default="var/beir", help="Dataset cache + results dir")
    p.add_argument("--device", default="cpu",
                   help="Torch device for the models (default cpu; mps OOMs the reranker on small machines)")
    p.add_argument("--no-mlflow", action="store_true")
    args = p.parse_args()

    rows = []
    for dataset_name in args.datasets:
        print(f"\n=== {dataset_name} ===")
        print(f"{'config':<16}{'nDCG@10':>9}{'Recall@100':>12}{'MRR':>7}{'MAP':>7}")
        for config in args.configs:
            report = run_beir(dataset_name, config, top_k=args.top_k, out_dir=args.out, device=args.device)
            rows.append(report)
            print(f"{config:<16}{report['ndcg@10']:>9.3f}{report['recall@100']:>12.3f}"
                  f"{report['mrr']:>7.3f}{report['map']:>7.3f}")
            if not args.no_mlflow:
                log_beir_run(report)

    os.makedirs(args.out, exist_ok=True)
    out_json = os.path.join(args.out, "beir_results.json")
    with open(out_json, "w") as f:
        json.dump(rows, f, indent=2)
    print(f"\nwrote {out_json}")
    if not args.no_mlflow:
        print(f"logged {len(rows)} runs to MLflow experiment '{EXPERIMENT_NAME}' (run `mlflow ui`)")


if __name__ == "__main__":
    main()
