import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from src.evaluation.scale import measure_cell

REPO = Path(__file__).resolve().parent.parent
METRIC_KEYS = (
    "build_time_s", "mem_rss_mb", "latency_p50_ms", "latency_p95_ms", "recall_at_k",
)


def test_exact_backends_have_near_perfect_recall():
    # numpy cosine and FAISS flat are exact, so recall vs brute force is ~1.0 (allow tiny
    # float32 boundary flips). Neither trains k-means, so they are safe to build in-process.
    for backend in ("numpy", "faiss-flat"):
        cell = measure_cell(backend, n=200, dim=32, queries=20, top_k=5, seed=0)
        assert cell["backend"] == backend
        assert cell["n"] == 200
        assert all(k in cell for k in METRIC_KEYS)
        assert cell["recall_at_k"] >= 0.95


def _run_worker(backend: str, n: int) -> dict:
    out = subprocess.run(
        [sys.executable, "scripts/benchmark_scale.py", "--worker",
         "--backend", backend, "--size", str(n), "--dim", "64",
         "--queries", "10", "--top-k", "5", "--seed", "0"],
        cwd=REPO, capture_output=True, text=True,
    )
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout.strip().splitlines()[-1])


def test_ivf_worker_runs_and_reports_nprobe():
    # FAISS IVF trains k-means; run it via the subprocess worker (as the real sweep does) to
    # avoid the macOS multi-OpenMP crash that happens when sklearn has been used in-process.
    cell = _run_worker("faiss-ivf", 1000)
    assert 0.0 <= cell["recall_at_k"] <= 1.0
    assert cell["nprobe"] is not None and cell["nprobe"] >= 1
    assert all(k in cell for k in METRIC_KEYS)


def test_structured_data_path_loads_from_hdf5(tmp_path):
    # The ann-benchmarks path reads a cached HDF5 (no download when the file already exists).
    h5py = pytest.importorskip("h5py")
    rng = np.random.default_rng(0)
    with h5py.File(tmp_path / "glove-100-angular.hdf5", "w") as f:
        f["train"] = rng.standard_normal((400, 16)).astype("float32")
        f["test"] = rng.standard_normal((20, 16)).astype("float32")
    cell = measure_cell(
        "faiss-flat", n=400, dim=16, queries=20, top_k=5, seed=0,
        data="glove-100-angular", data_dir=str(tmp_path),
    )
    assert cell["data"] == "glove-100-angular"
    assert cell["n"] == 400 and cell["dim"] == 16  # actual sizes come from the data
    assert cell["recall_at_k"] >= 0.95  # faiss-flat is exact
