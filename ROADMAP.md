# RAG Project Roadmap

A from-scratch RAG pipeline built incrementally. Each version groups a few atomic improvements; items keep stable letter codes for cross-reference. Each item ends with a `(difficulty: skills)` tag. Check items off as they land.

---

## V1: Repo-ready baseline (done)

**Goal:** a clean, reproducible, documented repo anyone can clone and run.

- [x] **README.** Project description, 5-stage architecture overview, setup (venv + pip + Ollama), usage examples.
- [x] **Centralized config** (`src/config.py`). One dataclass holding every constant (paths, models, chunk sizes, top_k, backend); all modules read from it.
- [x] **Error handling.** Graceful failures for bad PDFs, Ollama/OpenAI connection errors, and embedding OOM, each with a clear message.
- [x] **CLI** (`main.py`). An `argparse` entry point (`--query`, `--backend`, `--top-k`, `--no-rag`, and more) replacing the hardcoded query.
- [x] **Repo hygiene.** `.gitignore`, pinned `requirements.txt`, `.env.example`, and package `__init__.py` files.
- [x] **A. NumPy + JSON persistence.** Cache embeddings (`embeddings.npy`) and chunk metadata (`chunks.json`); on startup load from cache instead of re-embedding. *(Low: NumPy I/O, caching)*

---

## V2: Persistent and observable (done)

**Theme:** stop re-computing everything on every run; add observability.

**Why:** D upgrades both stores (FAISS replaces brute-force cosine with ANN search, and SQLite replaces the JSON file so chunks can be inserted or deleted individually). B, C, and E add observability and correctness guarantees.

- [x] **B. Proper logging.** Replace every `print()` with the `logging` module, configurable via `--log-level`. *(Low: Python logging)*
- [x] **C. Type hints.** Type annotations on all functions in `src/`. *(Low: Python typing)*
- [x] **D. SQLite + FAISS.** FAISS `IndexFlatIP` for ANN search; SQLite text store so individual chunks can be inserted or deleted without a full rebuild. *(Medium: vector indexing, FAISS, SQLite)*
- [x] **E. Unit tests.** `tests/` with pytest: chunking overlap, embedding shape, retrieval ranking. *(Medium: pytest, test design)*

---

## V3: Better extraction (done)

**Theme:** fix the data layer before improving retrieval.

**Why:** the old pypdf extractor lost multi-column layout, tables, and section headers, noise that degrades every downstream step. Cleaning extraction first means V4 operates on better input.

- [x] **F. Multiple file types.** Ingest `.txt`, `.md`, and `.docx` alongside PDF. *(Low: file I/O)*
- [x] **G. Extraction test data.** A hand-crafted fixture PDF (table with known cells, two-column section, labelled headers) with exact-content pytest assertions, plus annotated real-PDF integration checks. *(Low: test fixtures, pytest, ground-truth annotation)*
- [x] **H. Better PDF extraction.** `pdfplumber` layout-aware extraction: multi-column reading order, tables as Markdown, labelled section headers. *(Medium: PDF parsing, layout analysis, pdfplumber)*
- [x] **AB. Docstrings.** One-line docstrings on all public functions. *(Low: documentation habit)*

---

## V4: Better retrieval (done)

**Theme:** replace naive cosine similarity with a stronger retrieval stack.

**Why:** these are pure retrieval-algorithm improvements that sit on top of the existing FAISS + SQLite stack, with no infrastructure changes.

- [x] **I. HyDE.** Embed an LLM-generated hypothetical answer passage instead of the raw query; improves recall for short or ambiguous queries with no index changes. *(Low: query augmentation, retrieval quality)*
- [x] **K. BM25 retrieval.** Add `rank_bm25` as a second retrieval method alongside dense. *(Medium: sparse retrieval, lexical search)*
- [x] **L. Hybrid retrieval.** Fuse BM25 and dense scores via RRF or weighted sum. *(Medium: hybrid search, score fusion)*
- [x] **M. Re-ranking.** A cross-encoder (`ms-marco-MiniLM-L-6-v2`) re-scores the top-k results. *(Medium: cross-encoders, two-stage retrieval)*

---

## V5: Evaluation (done)

**Theme:** systematic benchmarking to quantify the impact of every design choice.

**Why:** R sweeps each config dimension and writes side-by-side answers for manual review (qualitative). O adds numeric scoring with MLflow tracking so runs are comparable across changes (quantitative).

- [x] **R. Evaluation pipeline.** Sweep all config dimensions (RAG vs no-RAG, retriever, fusion, reranking, embedding model, top_k, chunk size) against the 32 Q/A pairs; write side-by-side answer tables per dimension for manual review. *(Medium: evaluation, ablation studies)*
- [x] **O. MLflow experiment tracking.** A `keywords` field per QA pair plus `_score_answer()` produce a numeric `accuracy_29` (3 prose-only questions excluded); MLflow logs config params, accuracy, and latency per run; an LLM-as-judge (API model, not the local LLM) logs `score_judge` to catch keyword false positives and negatives. *(Medium: MLflow, experiment tracking, LLM-as-judge)*

---

## V6: Serving and demo

**Theme:** turn the pipeline into a demo-able product with an API and a visual interface.

**Why:** S exposes the pipeline as a REST API; U wraps it in a browser UI. U depends on S, since the dashboard calls the API rather than the pipeline directly.

- [x] **S. FastAPI server.** Endpoints: `POST /query` (run the pipeline, return JSON), `POST /evaluate` (run a fixed question set, return metrics), `POST /compare` (same query across two configs, both results), plus `GET /health` and `GET /presets`. *(Medium: REST APIs, async Python)*
- [x] **U. Streamlit dashboard.** Browser UI (`dashboard/`) over the API: run queries live and show retrieved chunks, compare two configs (RAG vs no-RAG) side-by-side, and chart evaluation metrics from MLflow plus an optional live run. *(Medium: Streamlit, frontend ML tools)*

---

## V7: Chatbot features

**Theme:** make it feel like a real conversational assistant.

**Why:** P makes responses feel live instead of waiting for the full generation; T lets follow-up questions reference earlier turns. Neither needs infrastructure changes.

- [x] **P. Streaming LLM output.** Stream tokens as they are generated across the CLI (stdout), the API (`POST /query/stream`, NDJSON), and the Streamlit dashboard, instead of waiting for the full response. *(Low: generator patterns, streaming APIs)*
- [x] **T. Conversation memory.** Client-managed chat history (Streamlit session) sent with each request; the stateless server condenses a follow-up into a standalone query before retrieval so context-dependent questions work. New `Chat` dashboard page. *(Medium: stateful pipelines)*

---

## V8: Vector database backend (done)

**Theme:** add Qdrant as a third dense backend alongside numpy and FAISS.

**Why:** Qdrant handles vectors, metadata, and CRUD in one service. Adding it as a selectable dense store (`numpy` / `faiss` / `qdrant`) makes metadata filtering first-class while leaving the existing backends in place as options. Q requires J.

- [x] **J. Qdrant vector database.** Add a `store=qdrant` dense backend selectable via config: store each chunk as a point `{id, vector, payload}` with text and source in the payload. Dense-only at first; numpy and FAISS stay as alternatives. In-process by default; `QDRANT_URL` connects to a persistent server and reuses an existing collection (no re-upsert) so it stays fast at scale. *(Medium: vector databases, Qdrant)*
- [x] **Q. Metadata filtering.** Let `retriever.retrieve()` filter by source before ranking; native via Qdrant payload filters, and supported across the numpy / FAISS / BM25 / hybrid backends too. *(Low: metadata, search filters)*

---

## V9: Production

**Theme:** production hardening and deployment.

**Why:** W is intentionally last, packaging the complete project once everything else is settled so anyone can run it with a single command.

- [ ] **W. Docker.** `Dockerfile` + `docker-compose.yml` bundling the app and Ollama. *(Medium: containers)*
