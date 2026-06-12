#!/usr/bin/env python3
"""CLI for the eval dimensions (see src/evaluation/report.py for the logic).

Usage:
    python scripts/eval.py --dimension rag_vs_norag
    python scripts/eval.py --all
"""

import argparse
import logging
import sys
import time
from pathlib import Path

# Allow imports from project root.
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation.dimensions import DIMENSIONS
from src.evaluation.report import run_dimension

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s — %(message)s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run eval dimensions against QA pairs.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dimension", choices=list(DIMENSIONS.keys()), help="Run one dimension")
    group.add_argument("--all", action="store_true", help="Run all dimensions sequentially")
    args = parser.parse_args()

    dims = list(DIMENSIONS.keys()) if args.all else [args.dimension]
    timings: list[tuple[str, float]] = []
    total_t0 = time.time()
    for name in dims:
        d = DIMENSIONS[name]
        t0 = time.time()
        run_dimension(name, d["labels"], d["configs"])
        elapsed = time.time() - t0
        timings.append((name, elapsed))
        print(f"  [{name}] total: {elapsed:.0f}s ({elapsed/60:.1f}min)", flush=True)

    if len(timings) > 1:
        total = time.time() - total_t0
        print(f"\n=== Runtime summary ===")
        for name, elapsed in timings:
            print(f"  {name:<20} {elapsed/60:6.1f} min")
        print(f"  {'TOTAL':<20} {total/60:6.1f} min")


if __name__ == "__main__":
    main()
