#!/usr/bin/env python3
"""CLI for the synthetic scaling benchmark (logic in src/evaluation/scale.py).

Sweeps each dense backend over a range of N and measures build time, memory, query latency
(p50/p95), and recall@k vs exact. Each (backend, N) cell runs in its own subprocess so the
memory number is clean and large N does not accumulate across cells.

Usage:
    python scripts/benchmark_scale.py
    python scripts/benchmark_scale.py --sizes 1000 10000 100000 1000000 --no-mlflow
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation.scale import (
    BACKENDS,
    EXPERIMENT_NAME,
    log_scale_run,
    make_chart,
    measure_cell,
)


def _run_worker(args: argparse.Namespace) -> None:
    """Internal mode: measure one cell and print it as a JSON line."""
    cell = measure_cell(args.backend, args.size, args.dim, args.queries, args.top_k, args.seed)
    print(json.dumps(cell))


def _run_sweep(args: argparse.Namespace) -> None:
    """Run every (backend, size) cell in a subprocess, then log to MLflow and chart."""
    backends = list(args.backends)
    qdrant_url = args.qdrant_url or os.environ.get("QDRANT_URL")
    if "qdrant" in backends and not qdrant_url:
        print(
            "skipping qdrant: it needs a running server. Start one "
            "(`docker compose -f docker/docker-compose.yml up -d qdrant`) and pass "
            "--qdrant-url http://localhost:6333 (or set QDRANT_URL). ':memory:' is brute force, "
            "not representative."
        )
        backends = [b for b in backends if b != "qdrant"]
    worker_env = {**os.environ, "QDRANT_URL": qdrant_url} if qdrant_url else None

    rows = []
    for backend in backends:
        for n in args.sizes:
            print(f"== {backend} N={n} ...", flush=True)
            cmd = [
                sys.executable, __file__, "--worker",
                "--backend", backend, "--size", str(n),
                "--dim", str(args.dim), "--queries", str(args.queries),
                "--top-k", str(args.top_k), "--seed", str(args.seed),
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True, env=worker_env)
            if proc.returncode != 0:
                print(f"   FAILED ({backend} N={n}):\n{proc.stderr.strip()[-600:]}")
                continue
            cell = json.loads(proc.stdout.strip().splitlines()[-1])
            rows.append(cell)
            mem = f"{cell['mem_rss_mb']:.0f}MB" if cell["mem_rss_mb"] is not None else "n/a (server)"
            print(
                f"   build={cell['build_time_s']:.2f}s mem={mem} "
                f"p50={cell['latency_p50_ms']:.2f}ms p95={cell['latency_p95_ms']:.2f}ms "
                f"recall={cell['recall_at_k']:.3f}"
            )
            if not args.no_mlflow:
                log_scale_run(cell)

    if not rows:
        print("no cells succeeded; nothing to chart.")
        return
    png = make_chart(rows, args.out)
    print(f"\nchart -> {png}")
    if not args.no_mlflow:
        print(f"logged {len(rows)} runs to MLflow experiment '{EXPERIMENT_NAME}' (run `mlflow ui`)")


def main() -> None:
    p = argparse.ArgumentParser(description="Synthetic scaling benchmark across dense backends.")
    p.add_argument("--backends", nargs="+", default=list(BACKENDS), choices=list(BACKENDS),
                   help="Backends to sweep (default: all four)")
    p.add_argument("--sizes", nargs="+", type=int, default=[1000, 5000, 20000, 100000],
                   help="Vector counts to sweep (default fits a laptop; big N is slower/heavier)")
    p.add_argument("--dim", type=int, default=384, help="Embedding dimension (384 = all-MiniLM)")
    p.add_argument("--queries", type=int, default=100, help="Query vectors for latency/recall")
    p.add_argument("--top-k", type=int, default=10)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", default="var/scale", help="Output dir for scale.png + scale_results.json")
    p.add_argument("--qdrant-url", default=None,
                   help="Qdrant server URL (default: $QDRANT_URL). Required for the qdrant backend; "
                        "without it qdrant is skipped (':memory:' is brute force, not representative)")
    p.add_argument("--no-mlflow", action="store_true", help="Skip MLflow logging")
    # Internal worker flags (one cell per subprocess).
    p.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    p.add_argument("--backend", help=argparse.SUPPRESS)
    p.add_argument("--size", type=int, help=argparse.SUPPRESS)
    args = p.parse_args()

    if args.worker:
        _run_worker(args)
    else:
        _run_sweep(args)


if __name__ == "__main__":
    main()
