# RAG Pipeline Design Notes

> **Note:** This is a synthetic document created for RAG demonstration and testing purposes.
> All benchmark numbers, dates, and configuration values are invented and do not reflect real experimental results.

Internal technical notes for the from-scratch RAG pipeline.

---

## Embedding Model Benchmarks

The following retrieval quality scores were measured on a fixed 47-question evaluation set covering the NLP/LLM paper corpus. Metric is top-5 Exact Match (chunk containing the gold answer is in the top-5 retrieved results).

| Model | Params | Dim | Top-5 EM | Avg latency (ms) |
|---|---|---|---|---|
| all-MiniLM-L6-v2 | 22M | 384 | 0.743 | 18 |
| bge-small-en-v1.5 | 33M | 384 | 0.761 | 21 |
| all-mpnet-base-v2 | 109M | 768 | 0.779 | 54 |
| bge-base-en-v1.5 | 109M | 768 | 0.787 | 57 |

**Decision:** `all-MiniLM-L6-v2` was selected as the default because the 4.4-point quality gap versus `bge-base-en-v1.5` did not justify a 3× latency increase for a local, single-user pipeline.

---

## Chunking Configuration

Three strategies were prototyped before settling on the tiktoken-based approach:

- **Naive character split** (`chunk_text`): simple but splits mid-sentence; retrieval quality dropped to 0.641 top-5 EM on the eval set.
- **Sentence split** (`chunk_text_by_sentence`): better coherence but high variance in chunk size (shortest: 12 tokens, longest: 891 tokens); FAISS index quality degrades with very short chunks.
- **Tiktoken accumulation** (`chunk_text_tiktoken`): splits by sentence then accumulates up to a token budget. Selected.

Final configuration:
```python
CHUNK_MAX_TOKENS = 128   # changed from 256 in V2-D after eval; smaller chunks improved precision
CHUNK_OVERLAP    = 50    # 39% overlap; higher values did not improve recall beyond this point
```

The 128-token max (down from the roadmap's initial 256) was determined empirically: at 256, the top-5 EM was 0.698; at 128 it rose to 0.743. The sweet spot appears to be around 100–150 tokens for this corpus size (~4,200 chunks total at 128 tokens).

---

## Retrieval Backend Comparison

Both backends were benchmarked on the same 47-question eval set with the corpus fully indexed.

| Backend | Index type | Top-5 EM | Index build (s) | Query latency (ms) |
|---|---|---|---|---|
| NumPy cosine | — | 0.743 | 1.2 | 34 |
| FAISS | IndexFlatIP | 0.743 | 0.8 | 4 |
| FAISS | IndexIVF (nlist=32) | 0.736 | 1.1 | 1 |

`IndexFlatIP` and NumPy produce identical results (exact search); IVF trades 0.7 EM points for a 4× query speedup. At the current corpus size (~4,200 chunks), the speedup is irrelevant — IVF only becomes worthwhile above ~100,000 chunks. Default was kept as `IndexFlatIP`.

---

## Prompt Template Design

Two prompt templates are maintained: one for RAG mode (context injected), one for no-RAG baseline. They are intentionally symmetric in length and framing so that any quality difference is attributable to the retrieved context, not prompt wording.

Key constraint discovered in testing: if the context passages are prepended without explicit attribution ("Source: X"), the model occasionally hallucinates a source or ignores the context entirely. Adding 'Source: {source}' before each passage reduced hallucinations on the eval set from 11/47 (23%) to 3/47 (6%).

---

## Storage Layer

### V1 — NumPy + JSON
- Embeddings saved to `cache/embeddings.npy` (float32, shape `[N, 384]`)
- Chunk text and metadata saved to `cache/chunks.json`
- Loading from cache: ~0.3s vs ~18s for re-embedding on the full corpus. Effectively mandatory.

### V2 — FAISS + SQLite
- `IndexFlatIP` persisted to `cache/faiss.index` via `faiss.write_index`
- Chunk text stored in SQLite (`cache/chunks.db`) so individual chunks can be inserted/deleted without full rebuild
- Migration from V1 to V2 was a one-time rebuild (no incremental path)
- Dual-store sync risk: FAISS index and SQLite must stay in lock-step. A Qdrant migration (roadmap item J) would eliminate this.


---

## Changelog

- **2025-11-04** — V1 complete. NumPy cache implemented. Embedding time reduced from 18s to 0.3s on second run.
- **2025-11-18** — Switched default chunking from naive character split to tiktoken accumulation after eval score rose from 0.641 to 0.743.
- **2025-12-09** — V2 complete. FAISS + SQLite backend added behind `--store faiss` flag. IVF index added as `--index-type ivf`. Unit tests added (pytest, 6 test files).
- **2026-01-15** — Reduced `CHUNK_MAX_TOKENS` from 256 to 128 after eval showing precision improvement. Cache invalidated and rebuilt.
- **2026-03-02** — Source attribution added to RAG prompt template after confabulation analysis on eval set.
