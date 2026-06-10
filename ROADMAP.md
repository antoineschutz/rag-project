# RAG Project — Versioned Roadmap

## V1 — Repo-ready baseline (push to GitHub)

**Goal:** A clean, reproducible, documented repo that anyone can clone and run.

### Checklist

#### 1. README.md
- [x] Project description, architecture overview (5 stages), setup instructions (venv + pip + Ollama), usage examples

#### 2. Centralized config (`src/config.py`)
- [x] A single dataclass holding all scattered constants: `DATA_PATH`, `EMBED_MODEL`, `CHUNK_MAX_TOKENS`, `CHUNK_OVERLAP`, `TOP_K`, `LLM_BACKEND`, `OLLAMA_MODEL`, `OPENAI_MODEL`, `CACHE_DIR`
- [x] Update all modules to read from config: `main.py`, `src/chunking/chunk.py`, `src/embeddings/embed.py`, `src/retrieval/retriever.py`, `src/llm/client.py`

#### 3. Basic error handling
- [x] `src/ingestion/loader.py`: wrap `PdfReader` in try/except, skip and warn on bad PDFs
- [x] `src/llm/client.py`: catch connection errors for Ollama/OpenAI with a clear message
- [x] `src/embeddings/embed.py`: catch OOM on `encode()`

#### 4. CLI entry point (refactor `main.py`)
- [x] `argparse` with: `--query`, `--data-path`, `--backend`, `--model`, `--top-k`, `--no-rag`
- [x] Replaces the hardcoded query in `main.py`

#### 5. Fix model name in `src/llm/client.py`
- [x] Replace `"gpt-4.1-mini"` with `"gpt-4o-mini"` (valid current OpenAI model name)

#### 6. Repo hygiene (pre-push)
- [x] Create `.gitignore` — exclude `venv/`, `__pycache__/`, `*.pyc`, `*.pyo`, `.DS_Store`, `data/*.pdf`, `.env`, `cache/`, `tmp/`
- [x] Create `requirements.txt` with pinned versions for: `pypdf`, `nltk`, `tiktoken`, `sentence-transformers`, `numpy`, `scikit-learn`, `ollama`, `openai`
- [x] Create `.env.example` documenting `OPENAI_API_KEY=your_key_here`
- [x] Add `__init__.py` to `src/`, `src/ingestion/`, `src/chunking/`, `src/embeddings/`, `src/retrieval/`, `src/prompts/`, `src/llm/`

#### 7. Embedding persistence (NumPy + JSON)
- [x] After embedding, save vectors to `cache/embeddings.npy` and chunk metadata to `cache/chunks.json`
- [x] On startup, check for cache files and skip re-embedding if present
- [x] Add `CACHE_DIR` to `src/config.py`

### Verification (pre-push)
1. `git init && git add . && git status` — confirm `venv/`, `.pyc`, `.DS_Store` are excluded
2. `pip install -r requirements.txt` in a fresh venv — confirm all deps install
3. `python main.py --query "What is Galois theory?"` — confirm CLI works
4. `python main.py --backend openai --query "test"` — confirm clear error if `OPENAI_API_KEY` not set
5. Confirm clean error on missing Ollama rather than a crash
6. Run `python main.py` twice — confirm second run logs "loading from cache" and skips embedding

---

## Improvement catalogue

Atomic improvements that can be combined into future versions. Check off each item when complete. Grouped by version, sorted by difficulty within each group.

### V1 (done)
- [x] **A — NumPy + JSON persistence** — save embeddings to `cache/embeddings.npy` and chunk text/metadata to `cache/chunks.json`; on startup load from cache instead of re-embedding; eliminates the re-embedding bottleneck on every run *(Low — NumPy I/O, caching)*

### V2 (done)
- [x] **B — Proper logging** — replace all `print()` with Python `logging` module, configurable via `--log-level` *(Low — Python logging)*
- [x] **C — Type hints** — add type annotations to all functions in `src/` *(Low — Python typing)*
- [x] **D — SQLite + FAISS** — replace sklearn cosine similarity with FAISS `IndexFlatIP` for ANN search; replace JSON text store with SQLite so individual chunks can be inserted or deleted without rebuilding from scratch *(Medium — Vector indexing, FAISS, SQLite)*
- [x] **E — Unit tests** — `tests/` directory with pytest: chunking overlap, embedding shape, retrieval ranking *(Medium — pytest, test design)*

### V3
- [x] **F — Multiple file types** — support `.txt`, `.md`, `.docx` ingestion alongside PDF *(Low — File I/O)*
- [x] **G — Extraction test data** — (a) create a synthetic hand-crafted PDF (`tests/fixtures/extraction_test.pdf`) containing a table with known cell values, a two-column section, and labelled headers; write pytest assertions that exact expected text/table content is extracted; (b) annotate key sections of `data/rag_lewis2020.pdf` with expected extraction output and write integration-level assertions *(Low — Test fixtures, pytest, ground-truth annotation)*
- [x] **H — Better PDF extraction** — replace pypdf's basic `page.extract_text()` with `pdfplumber` for layout-aware extraction: detect and preserve multi-column reading order, extract tables as Markdown, retain section headers as labelled elements; update `src/ingestion/loader.py` *(Medium — PDF parsing, layout analysis, pdfplumber)*
- [x] **AB — Docstrings** — add one-line docstrings to all public functions *(Low — Documentation habit)*

### V4
- [x] **I — HyDE (Hypothetical Document Embeddings)** — before embedding a query, prompt the LLM to generate a hypothetical answer passage and embed that instead of the raw query string; improves recall for short or ambiguous queries with no index changes; requires the LLM to be available at query time *(Low — Query augmentation, retrieval quality)*
- [x] **K — BM25 retrieval** — add `rank_bm25` as a second retrieval method alongside cosine similarity *(Medium — Sparse retrieval, lexical search)*
- [x] **L — Hybrid retrieval** — combine BM25 and dense scores (RRF or weighted sum) *(Medium — Hybrid search, score fusion)*
- [x] **M — Re-ranking** — add a cross-encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`) to re-score top-k results *(Medium — Cross-encoders, two-stage retrieval)*
### V5
- [x] **R — Evaluation pipeline** — run all config dimensions against the 32 Q/A pairs in `docs/eval_qa_pairs.md`: RAG vs no-RAG, retrieval method (dense/BM25/hybrid), fusion strategy (RRF vs weighted sum), reranking (on/off), and embedding model (all-MiniLM-L6-v2, bge-small-en, e5-small); report answers side-by-side per comparison dimension for manual review *(Medium — Evaluation, ablation studies)*
- [x] **O — MLflow experiment tracking** — add a `keywords` field to each QA pair (dropping Q4, Q14, Q19 which are prose explanations not suited to string matching) and a `_score_answer()` function that checks for required substrings to produce a numeric accuracy score over 29 questions; integrate MLflow to log config parameters, `accuracy_29`, and per-config latency for every run so results are comparable across pipeline changes; add an LLM-as-judge safeguard (API model, not the local LLM) that runs alongside keyword scoring and logs `score_judge` to surface disagreements and catch false positives/negatives *(Medium — MLflow, experiment tracking, LLM-as-judge)*

### V6
- [ ] **S — FastAPI server** — expose four endpoints: `POST /upload` (ingest a document), `POST /query` (run the RAG pipeline and return JSON), `POST /evaluate` (run a fixed question set and return metrics), `POST /compare` (run the same query across two configs and return both results side-by-side) *(Medium — REST APIs, async Python)*
- [ ] **U — Streamlit dashboard** — web UI to run queries live, display retrieved chunks, compare RAG vs no-RAG side-by-side, and visualise evaluation metrics (latency, retrieval scores) *(Medium — Streamlit, frontend ML tools)*

### V7
- [ ] **P — Streaming LLM output** — stream Ollama/OpenAI tokens to stdout instead of waiting for full response *(Low — Generator patterns, streaming APIs)*
- [ ] **T — Conversation memory** — maintain chat history so follow-up questions work in context *(Medium — Stateful pipelines)*

### V8
- [ ] **J — Qdrant vector database** — replace FAISS + SQLite with a Qdrant collection; each chunk stored as a point `{id, vector, payload}` where payload holds text and source; eliminates the dual-store sync problem and enables metadata filtering (Q) as a first-class feature *(Medium — Vector databases, Qdrant)*
- [ ] **Q — Metadata filtering** — allow `retriever.retrieve()` to filter by source before ranking; straightforward with Qdrant payload filters, awkward without it *(Low — Metadata, search filters)*

### V9
- [ ] **V — Web ingestion** — `requests` + `BeautifulSoup` scraper as a third data source *(Medium — Web scraping)*
- [ ] **W — Docker** — `Dockerfile` + `docker-compose.yml` bundling app + Ollama *(Medium — Containers)*
- [ ] **AA — Async pipeline** — `asyncio`-based ingestion and embedding for parallel processing *(High — Async Python)*

---

## V2 — Persistent & observable (done)

**Theme:** Stop re-computing everything on every run; add observability.

**Why:** SQLite + FAISS (D) upgrades both stores — FAISS replaces brute-force cosine similarity with proper ANN search, and SQLite replaces the JSON file so chunks can be inserted or deleted individually. Logging (B), type hints (C), and tests (E) add observability and correctness guarantees.

### Checklist
- [x] **B** — Proper logging
- [x] **C** — Type hints
- [x] **D** — SQLite + FAISS
- [x] **E** — Unit tests

---

## V3 — Better extraction (done)

**Theme:** Fix the data layer before improving retrieval.

**Why:** The current pypdf extractor loses multi-column layout, tables, and section headers — noise that degrades every downstream step. Cleaning extraction and broadening ingest file types here means V4 (retrieval) operates on significantly better input.

### Checklist
- [x] **F** — Multiple file types
- [x] **G** — Extraction test data
- [x] **H** — Better PDF extraction
- [x] **AB** — Docstrings

---

## V4 — Better retrieval

**Theme:** Replace naive cosine similarity with a state-of-the-art retrieval stack.

**Why:** K, L, and M are pure retrieval algorithm improvements that work directly on top of the existing FAISS + SQLite stack — no infrastructure changes required.

### Checklist
- [x] **I** — HyDE
- [x] **K** — BM25 retrieval
- [x] **L** — Hybrid retrieval
- [x] **M** — Re-ranking

---

## V5 — Evaluation

**Theme:** Systematic benchmarking to quantify the impact of every design choice.

**Why:** R uses the existing 32 Q/A pairs in `docs/eval_qa_pairs.md` to run all config comparisons and produces side-by-side text answers for manual review — no judge LLM needed. O complements it with a handcrafted fictional-universe MCQ dataset that gives clean numeric accuracy scores (the LLM has zero prior knowledge of the content, so correct answers prove retrieval worked) and logs accuracy + per-stage latency to MLflow for cross-run comparison.

### Checklist
- [ ] **R** — Evaluation pipeline
- [ ] **O** — MCQ benchmark + MLflow

---

## V6 — Serving & demo

**Theme:** Turn the pipeline into a demo-able product with an API and visual interface.

**Why:** FastAPI (S) exposes the pipeline as a REST API with upload, query, evaluate, and compare endpoints. Streamlit (U) wraps it in a browser UI for live demos. U depends on S — the dashboard calls the API rather than the pipeline directly.

### Checklist
- [ ] **S** — FastAPI server
- [ ] **U** — Streamlit dashboard

---

## V7 — Chatbot features

**Theme:** Make it feel like a real conversational assistant.

**Why:** Streaming (P) makes responses feel live rather than waiting for the full generation. Conversation memory (T) lets follow-up questions reference earlier turns. Neither requires infrastructure changes — both work on top of the existing pipeline.

### Checklist
- [ ] **P** — Streaming LLM output
- [ ] **T** — Conversation memory

---

## V8 — Infrastructure upgrade

**Theme:** Replace the dual FAISS+SQLite store with a proper vector database.

**Why:** Qdrant (J) handles vectors, metadata, and CRUD in one service, eliminating the dual-store sync problem. Metadata filtering (Q) becomes a first-class feature via Qdrant payload filters. Q strictly requires J.

### Checklist
- [ ] **J** — Qdrant vector database
- [ ] **Q** — Metadata filtering

---

## V9 — Production

**Theme:** Production hardening and deployment.

**Why:** Web ingestion (V) expands data sources beyond local files. Async (AA) handles real concurrent workloads. Docker (W) is intentionally last — it packages the complete project once everything else is settled.

### Checklist
- [ ] **V** — Web ingestion
- [ ] **W** — Docker
- [ ] **AA** — Async pipeline
