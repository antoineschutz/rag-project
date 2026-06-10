#!/usr/bin/env python3
"""Evaluation pipeline — runs Q/A pairs against comparison dimensions.

Usage:
    python scripts/eval.py --dimension rag_vs_norag
    python scripts/eval.py --all
"""

import argparse
import hashlib
import json
import logging
import shutil
import sys
import time
from pathlib import Path
from typing import Any

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import config
from src.embeddings.embed import Embedder
from main import run_pipeline

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s — %(message)s")

OUT_DIR = Path("eval_results2")
CACHE_FILE = OUT_DIR / ".llm_cache.json"


def _cache_key(query: str, cfg: dict) -> str:
    payload = json.dumps({"query": query, "cfg": cfg}, sort_keys=True)
    return hashlib.md5(payload.encode()).hexdigest()


def _load_cache() -> dict[str, str]:
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text())
    return {}


def _save_cache(cache: dict[str, str]) -> None:
    CACHE_FILE.write_text(json.dumps(cache, indent=2))

# ---------------------------------------------------------------------------
# Q/A pairs — fill in question / expected / source before running
# Level distribution: L1×5, L2×6, L3×2, L4×6, L5×5, L6×3, L7×2, L8×3
#
# `keywords`: lowercase substrings the auto-scorer (scripts/benchmark.py)
# checks for, case-insensitively, with AND semantics — an answer scores correct
# only if EVERY listed substring is present. An empty list ([]) means the
# question is excluded from automatic scoring (pure-prose answers that string
# matching can't judge); Q4, Q14, Q19 are dropped on that basis, leaving 29
# keyword-scored questions (accuracy_29). The LLM-as-judge safeguard runs
# alongside to catch keyword false positives/negatives.
# ---------------------------------------------------------------------------
QA_PAIRS: list[dict[str, Any]] = [
    # Level 1 — plain prose, md/docx
    {"id": 1,  "level": 1, "question": "Why was `all-MiniLM-L6-v2` chosen as the default embedding model over `bge-base-en-v1.5`?", "expected": "The 4.4-point quality gap did not justify a 3x latency increase (18 ms vs 57 ms) for a local, single-user pipeline.", "source": "rag_design_notes.md", "keywords": ["4.4"]},
    {"id": 2,  "level": 1, "question": "How much did adding source attribution to the RAG prompt reduce hallucination?", "expected": "From 11/47 (23%) to 3/47 (6%)", "source": "rag_design_notes.md", "keywords": ["23%", "6%"]},
    {"id": 3,  "level": 1, "question": "Above what corpus size does FAISS IVF become worthwhile over IndexFlatIP?", "expected": "Above approximately 100,000 chunks", "source": "rag_design_notes.md", "keywords": ["100,000"]},
    {"id": 4,  "level": 1, "question": "Why does BM25 fall further behind DPR on NaturalQuestions than on TriviaQA?", "expected": "NQ has longer, more paraphrastic questions with low lexical overlap between question and passage.", "source": "qa_benchmark_report.docx", "keywords": []},
    {"id": 5,  "level": 1, "question": "What generator model do RAG-Token and RAG-Sequence use?", "expected": "BART-large", "source": "qa_benchmark_report.docx", "keywords": ["bart"]},
    # Level 2 — tables in md/docx
    {"id": 6,  "level": 2, "question": "What top-5 Exact Match score does `all-MiniLM-L6-v2` achieve?", "expected": "0.743", "source": "rag_design_notes.md", "keywords": ["0.743"]},
    {"id": 7,  "level": 2, "question": "Which embedding model achieves the highest top-5 EM, and what is the score?", "expected": "`bge-base-en-v1.5` at 0.787", "source": "rag_design_notes.md", "keywords": ["bge-base", "0.787"]},
    {"id": 8,  "level": 2, "question": "What is the query latency of IndexFlatIP vs IndexIVF?", "expected": "IndexFlatIP: 4 ms, IndexIVF: 1 ms", "source": "rag_design_notes.md", "keywords": ["4 ms", "1 ms"]},
    {"id": 9,  "level": 2, "question": "What NQ Exact Match does RAG-Sequence achieve in the benchmark report?", "expected": "44.5 EM", "source": "qa_benchmark_report.docx", "keywords": ["44.5"]},
    {"id": 10, "level": 2, "question": "What NQ EM does DPR achieve with top-5 vs top-10 retrieval?", "expected": "41.5 (top-5) to 43.2 (top-10), a 1.7-point gain", "source": "qa_benchmark_report.docx", "keywords": ["41.5", "43.2"]},
    {"id": 11, "level": 2, "question": "Which system achieves the highest TriviaQA EM in the benchmark report?", "expected": "RAG-Sequence at 68.2 EM", "source": "qa_benchmark_report.docx", "keywords": ["68.2"]},
    # Level 3 — code blocks in md
    {"id": 12, "level": 3, "question": "What are the final `CHUNK_MAX_TOKENS` and `CHUNK_OVERLAP` values?", "expected": "`CHUNK_MAX_TOKENS = 128`, `CHUNK_OVERLAP = 50`", "source": "rag_design_notes.md", "keywords": ["128", "50"]},
    {"id": 13, "level": 3, "question": "What token overlap percentage does the current chunking configuration use?", "expected": "39% (50 overlap tokens out of 128 max)", "source": "rag_design_notes.md", "keywords": ["39%"]},
    # Level 4 — prose in PDFs
    {"id": 14, "level": 4, "question": "What is the difference between RAG-Token and RAG-Sequence?", "expected": "RAG-Sequence uses the same retrieved document for the entire output; RAG-Token marginalizes over documents at each generated token.", "source": "rag_lewis2020.pdf", "keywords": []},
    {"id": 15, "level": 4, "question": "What retriever does the RAG model use?", "expected": "Dense Passage Retrieval (DPR) with a bi-encoder", "source": "rag_lewis2020.pdf", "keywords": ["dpr"]},
    {"id": 16, "level": 4, "question": "What two pre-training tasks does BERT use?", "expected": "Masked Language Modeling (MLM) and Next Sentence Prediction (NSP)", "source": "bert_devlin2018.pdf", "keywords": ["masked language", "next sentence"]},
    {"id": 17, "level": 4, "question": "What percentage of input tokens are masked in BERT's MLM objective?", "expected": "15%", "source": "bert_devlin2018.pdf", "keywords": ["15%"]},
    {"id": 18, "level": 4, "question": "What type of masking does REALM use during pre-training, and why?", "expected": "Salient span masking: it masks named entities and dates rather than random tokens, forcing the model to retrieve factual knowledge.", "source": "realm_guu2020.pdf", "keywords": ["salient span"]},
    {"id": 19, "level": 4, "question": "What three reasons do Vaswani et al. give for preferring self-attention over recurrent layers?", "expected": "(1) Lower total computational complexity per layer, (2) more parallelizable computation, (3) shorter path length between long-range dependencies", "source": "attention_is_all_you_need.pdf", "keywords": []},
    # Level 5 — tables in PDFs
    {"id": 20, "level": 5, "question": "What BLEU score did ConvS2S Ensemble achieve on WMT 2014 English-to-French?", "expected": "41.29", "source": "attention_is_all_you_need.pdf", "keywords": ["41.29"]},
    {"id": 21, "level": 5, "question": "What is the training cost of the base Transformer model in floating point operations?", "expected": "3.3 x 10^18 FLOPs", "source": "attention_is_all_you_need.pdf", "keywords": ["3.3"]},
    {"id": 22, "level": 5, "question": "What is the QQP score achieved by BERT-LARGE on the GLUE benchmark?", "expected": "72.1", "source": "bert_devlin2018.pdf", "keywords": ["72.1"]},
    {"id": 23, "level": 5, "question": "What Exact Match score does REALM achieve on NaturalQuestions Open?", "expected": "40.4 EM", "source": "realm_guu2020.pdf", "keywords": ["40.4"]},
    {"id": 24, "level": 5, "question": "What Exact Match does RAG-Sequence achieve on NaturalQuestions in Lewis et al.?", "expected": "44.5 EM", "source": "rag_lewis2020.pdf", "keywords": ["44.5"]},
    # Level 6 — multi-column layout
    {"id": 25, "level": 6, "question": "How many attention heads and what model dimension does the Transformer base model use?", "expected": "8 heads, d_model = 512", "source": "attention_is_all_you_need.pdf", "keywords": ["512"]},
    {"id": 26, "level": 6, "question": "What feed-forward network dimension does the Transformer base model use?", "expected": "d_ff = 2048", "source": "attention_is_all_you_need.pdf", "keywords": ["2048"]},
    {"id": 27, "level": 6, "question": "What is BERT-LARGE's hidden size and number of attention heads?", "expected": "Hidden size 1024, 16 attention heads", "source": "bert_devlin2018.pdf", "keywords": ["1024", "16"]},
    # Level 7 — equations in PDFs
    {"id": 28, "level": 7, "question": "What scaling factor does scaled dot-product attention apply before the softmax?", "expected": "1/sqrt(d_k): divide by the square root of the key dimension", "source": "attention_is_all_you_need.pdf", "keywords": ["square root"]},
    {"id": 29, "level": 7, "question": "How does REALM compute the probability of retrieving document z given input x?", "expected": "p(z|x) proportional to exp(Embed_input(x) . Embed_doc(z)); top-k documents are found via Maximum Inner Product Search (MIPS).", "source": "realm_guu2020.pdf", "keywords": ["inner product"]},
    # Level 8 — cross-document retrieval
    {"id": 30, "level": 8, "question": "How does RAG (Lewis 2020) compare to REALM (Guu 2020) on NaturalQuestions Open?", "expected": "RAG-Sequence achieves 44.5 EM vs REALM's 40.4 EM, a difference of 4.1 points in favour of RAG.", "source": "rag_lewis2020.pdf + realm_guu2020.pdf", "keywords": ["44.5", "40.4"]},
    {"id": 31, "level": 8, "question": "How many more attention heads does BERT-BASE have compared to the base Transformer model?", "expected": "BERT-BASE uses 12 attention heads; the base Transformer uses 8, a difference of 4.", "source": "bert_devlin2018.pdf + attention_is_all_you_need.pdf", "keywords": ["12", "8"]},
    {"id": 32, "level": 8, "question": "How does RAG-Sequence (Lewis 2020) compare to REALM (Guu 2020) on WebQuestions?", "expected": "RAG-Sequence achieves 45.2 EM vs REALM's 40.7 EM; RAG outperforms REALM by 4.5 points on WebQuestions.", "source": "rag_lewis2020.pdf + realm_guu2020.pdf", "keywords": ["45.2", "40.7"]},
]

# ---------------------------------------------------------------------------
# Comparison dimensions
# ---------------------------------------------------------------------------
DIMENSIONS: dict[str, dict[str, Any]] = {
    "rag_vs_norag": {
        "labels": ["RAG (baseline)", "no-RAG"],
        "configs": [
            {
                "no_rag": False, "retriever": "dense",
                "embed_model": "all-MiniLM-L6-v2", "rerank": False, "top_k": 15,
            },
            {"no_rag": True},
        ],
    },
    "retrieval": {
        "labels": ["dense", "bm25", "hybrid-rrf"],
        "configs": [
            {
                "no_rag": False, "retriever": "dense",
                "embed_model": "all-MiniLM-L6-v2", "rerank": False, "top_k": 15,
            },
            {
                "no_rag": False, "retriever": "bm25",
                "rerank": False, "top_k": 15,
            },
            {
                "no_rag": False, "retriever": "hybrid", "fusion": "rrf", "alpha": 0.5,
                "embed_model": "all-MiniLM-L6-v2", "rerank": False, "top_k": 15,
            },
        ],
    },
    "fusion": {
        "labels": ["hybrid-rrf", "hybrid-weighted"],
        "configs": [
            {
                "no_rag": False, "retriever": "hybrid", "fusion": "rrf", "alpha": 0.5,
                "embed_model": "all-MiniLM-L6-v2", "rerank": False, "top_k": 15,
            },
            {
                "no_rag": False, "retriever": "hybrid", "fusion": "weighted", "alpha": 0.5,
                "embed_model": "all-MiniLM-L6-v2", "rerank": False, "top_k": 15,
            },
        ],
    },
    "reranking": {
        "labels": ["no rerank", "rerank"],
        "configs": [
            {
                "no_rag": False, "retriever": "dense",
                "embed_model": "all-MiniLM-L6-v2", "rerank": False, "top_k": 15,
            },
            {
                "no_rag": False, "retriever": "dense",
                "embed_model": "all-MiniLM-L6-v2", "rerank": True, "top_k": 15,
            },
        ],
    },
    "embed_model": {
        "labels": ["all-MiniLM-L6-v2", "bge-small-en", "e5-small", "bge-base", "bge-large"],
        "configs": [
            {
                "no_rag": False, "retriever": "dense",
                "embed_model": "all-MiniLM-L6-v2", "rerank": False, "top_k": 15,
            },
            {
                "no_rag": False, "retriever": "dense",
                "embed_model": "BAAI/bge-small-en-v1.5", "rerank": False, "top_k": 15,
            },
            {
                "no_rag": False, "retriever": "dense",
                "embed_model": "intfloat/e5-small-v2", "rerank": False, "top_k": 15,
            },
            {
                "no_rag": False, "retriever": "dense",
                "embed_model": "BAAI/bge-base-en-v1.5", "rerank": False, "top_k": 15,
            },
            {
                "no_rag": False, "retriever": "dense",
                "embed_model": "BAAI/bge-large-en-v1.5", "rerank": False, "top_k": 15,
            },
        ],
    },
    "top_k": {
        "labels": ["top_k=5", "top_k=15", "top_k=20", "top_k=30", "top_k=40", "top_k=60", "top_k=80", "top_k=100"],
        "configs": [
            {
                "no_rag": False, "retriever": "dense",
                "embed_model": "all-MiniLM-L6-v2", "rerank": False, "top_k": 5,
            },
            {
                "no_rag": False, "retriever": "dense",
                "embed_model": "all-MiniLM-L6-v2", "rerank": False, "top_k": 15,
            },
            {
                "no_rag": False, "retriever": "dense",
                "embed_model": "all-MiniLM-L6-v2", "rerank": False, "top_k": 20,
            },
            {
                "no_rag": False, "retriever": "dense",
                "embed_model": "all-MiniLM-L6-v2", "rerank": False, "top_k": 30,
            },
            {
                "no_rag": False, "retriever": "dense",
                "embed_model": "all-MiniLM-L6-v2", "rerank": False, "top_k": 40,
            },
            {
                "no_rag": False, "retriever": "dense",
                "embed_model": "all-MiniLM-L6-v2", "rerank": False, "top_k": 60,
            },
            {
                "no_rag": False, "retriever": "dense",
                "embed_model": "all-MiniLM-L6-v2", "rerank": False, "top_k": 80,
            },
            {
                "no_rag": False, "retriever": "dense",
                "embed_model": "all-MiniLM-L6-v2", "rerank": False, "top_k": 100,
            },
        ],
    },
    "chunk_max_tokens": {
        "labels": ["tokens=64", "tokens=128", "tokens=256", "tokens=512", "tokens=1024"],
        "configs": [
            {
                "no_rag": False, "retriever": "dense",
                "embed_model": "all-MiniLM-L6-v2", "rerank": False, "top_k": 15,
                "chunk_max_tokens": 64,
            },
            {
                "no_rag": False, "retriever": "dense",
                "embed_model": "all-MiniLM-L6-v2", "rerank": False, "top_k": 15,
                "chunk_max_tokens": 128,
            },
            {
                "no_rag": False, "retriever": "dense",
                "embed_model": "all-MiniLM-L6-v2", "rerank": False, "top_k": 15,
                "chunk_max_tokens": 256,
            },
            {
                "no_rag": False, "retriever": "dense",
                "embed_model": "all-MiniLM-L6-v2", "rerank": False, "top_k": 15,
                "chunk_max_tokens": 512,
            },
            {
                "no_rag": False, "retriever": "dense",
                "embed_model": "all-MiniLM-L6-v2", "rerank": False, "top_k": 15,
                "chunk_max_tokens": 1024,
            },
        ],
    },
    "best": {
        # Per-dimension winners stacked: RAG, hybrid+rrf, rerank, bge-small,
        # top_k=20, chunk_max_tokens=128. Baseline column is the canonical
        # dense/MiniLM/k=15 config (cached) for side-by-side comparison.
        "labels": ["best-combined", "baseline"],
        "configs": [
            {
                "no_rag": False, "retriever": "hybrid", "fusion": "rrf", "alpha": 0.5,
                "embed_model": "BAAI/bge-small-en-v1.5", "rerank": True, "top_k": 20,
                "chunk_max_tokens": 128,
            },
            {
                "no_rag": False, "retriever": "dense",
                "embed_model": "all-MiniLM-L6-v2", "rerank": False, "top_k": 15,
            },
        ],
    },
}


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run_dimension(name: str, labels: list[str], configs: list[dict]) -> None:
    active = [qa for qa in QA_PAIRS if qa["question"]]
    if not active:
        print(f"[{name}] No questions filled in — skipping.")
        return

    print(f"\n=== {name} ({len(active)} questions × {len(configs)} configs) ===")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{name}.md"

    model = config.OLLAMA_MODEL if config.LLM_BACKEND == "ollama" else config.OPENAI_MODEL

    # answers_matrix[q_idx][cfg_idx]
    answers_matrix: list[list[str]] = [[""] * len(configs) for _ in active]
    cache = _load_cache()

    cfg_times: list[float] = []
    for i, cfg in enumerate(configs):
        needs_embedder = not cfg.get("no_rag") and cfg.get("retriever", "dense") != "bm25"
        embedder: Embedder | None = None
        cfg_t0 = time.time()

        for j, qa in enumerate(active):
            key = _cache_key(qa["question"], cfg)
            if key in cache:
                print(f"    Q{qa['id']} [{labels[i]}] (cached)", flush=True)
                answers_matrix[j][i] = cache[key]
                continue

            if embedder is None and needs_embedder:
                print(f"\n  [{labels[i]}] loading embedder...", flush=True)
                embedder = Embedder(cfg.get("embed_model") or config.EMBED_MODEL)

            print(f"    Q{qa['id']} (level {qa['level']}) [{labels[i]}]...", flush=True)
            ans = run_pipeline(qa["question"], embedder=embedder, **cfg)
            answers_matrix[j][i] = ans
            cache[key] = ans
            _save_cache(cache)

        cfg_elapsed = time.time() - cfg_t0
        cfg_times.append(cfg_elapsed)
        print(f"  [{labels[i]}] done in {cfg_elapsed:.0f}s", flush=True)

    with open(out_path, "w") as f:
        f.write(f"# {name}\n\n")
        f.write(f"**backend:** {config.LLM_BACKEND} · **model:** {model}\n\n")
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Run eval dimensions against QA pairs.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dimension", choices=list(DIMENSIONS.keys()), help="Run one dimension")
    group.add_argument("--all", action="store_true", help="Run all dimensions sequentially")
    args = parser.parse_args()

    shutil.rmtree(Path(__file__).parent.parent / "cache", ignore_errors=True)

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
