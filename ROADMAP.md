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
- [ ] **J — Qdrant vector database** — replace FAISS + SQLite with a Qdrant collection; each chunk stored as a point `{id, vector, payload}` where payload holds text and source; eliminates the dual-store sync problem and enables metadata filtering (Q) as a first-class feature *(Medium — Vector databases, Qdrant)*
- [ ] **K — BM25 retrieval** — add `rank_bm25` as a second retrieval method alongside cosine similarity *(Medium — Sparse retrieval, lexical search)*
- [ ] **L — Hybrid retrieval** — combine BM25 and dense scores (RRF or weighted sum) *(Medium — Hybrid search, score fusion)*
- [ ] **M — Re-ranking** — add a cross-encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`) to re-score top-k results *(Medium — Cross-encoders, two-stage retrieval)*
### V5
- [ ] **P — Streaming LLM output** — stream Ollama/OpenAI tokens to stdout instead of waiting for full response *(Low — Generator patterns, streaming APIs)*
- [ ] **Q — Metadata filtering** — allow `retriever.retrieve()` to filter by source before ranking *(Low if J is done, Medium otherwise — Metadata, search filters)*
- [ ] **R — Evaluation framework** — run RAG and no-RAG on a fixed set of question-answer pairs, score each answer for correctness, and report results side-by-side *(Medium — RAG evaluation, metrics)*
- [ ] **N — Chunking strategy comparison** — run the eval set from R across naive/sentence/tiktoken chunkers and log scores; requires R *(Medium — Ablation studies)*
- [ ] **S — FastAPI server** — expose four endpoints: `POST /upload` (ingest a document), `POST /query` (run the RAG pipeline and return JSON), `POST /evaluate` (run a fixed question set and return metrics), `POST /compare` (run the same query across two configs and return both results side-by-side) *(Medium — REST APIs, async Python)*
- [ ] **T — Conversation memory** — maintain chat history so follow-up questions work in context *(Medium — Stateful pipelines)*
- [ ] **U — Streamlit dashboard** — web UI to run queries live, display retrieved chunks, compare RAG vs no-RAG side-by-side, and visualise evaluation metrics (latency, faithfulness, retrieval scores) *(Medium — Streamlit, frontend ML tools)*

### V6
- [ ] **V — Web ingestion** — `requests` + `BeautifulSoup` scraper as a third data source *(Medium — Web scraping)*
- [ ] **W — Docker** — `Dockerfile` + `docker-compose.yml` bundling app + Ollama *(Medium — Containers)*
- [ ] **X — Embedding model comparison** — swap the embedding model (`all-MiniLM-L6-v2`, `bge-small-en`, `e5-small`) on a fixed eval set and log retrieval quality scores; analogous to N (chunking comparison) but for the embedding dimension; requires R *(Medium — Model evaluation, ablation studies)*
- [ ] **Y — MLflow experiment tracking** — log each run's parameters (embedding model, chunk size, retrieval method) and metrics (retrieval score, faithfulness, latency) to MLflow so experiments from N, X, and R are comparable in a single UI *(Medium — MLflow, experiment tracking)*
- [ ] **Z — RAGAS evaluation** — plug in the `ragas` library for context precision/recall/faithfulness metrics *(High — RAG evaluation science)*
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

**Why:** BM25 (K), hybrid search (L), and re-ranking (M) are independent retrieval improvements that work on top of the existing FAISS + SQLite stack. Qdrant (J) is an optional infrastructure upgrade that collapses the dual-store into a single service with built-in persistence, CRUD, and metadata filtering — useful but not a prerequisite for K/L/M. Chunking ablations (N) moved to V5 because they require the evaluation framework (R) to be meaningful.

### Checklist
- [x] **I** — HyDE
- [ ] **J** — Qdrant vector database
- [ ] **K** — BM25 retrieval
- [ ] **L** — Hybrid retrieval
- [ ] **M** — Re-ranking

---

## V5 — Serving & evaluation

**Theme:** Turn the script into a real service you can benchmark and demo.

**Why:** Once retrieval quality is established (V4), build the interface around it. Evaluation (R) gives a quantitative story; FastAPI (S) makes it demo-able; streaming (P) makes it feel live; memory (T) makes it useful as a chatbot. Metadata filtering (Q) enables scoped retrieval over specific documents.

### Checklist
- [ ] **P** — Streaming LLM output
- [ ] **Q** — Metadata filtering
- [ ] **R** — Evaluation framework
- [ ] **N** — Chunking strategy comparison (requires R)
- [ ] **S** — FastAPI server
- [ ] **T** — Conversation memory
- [ ] **U** — Streamlit dashboard

---

## V6 — Production & advanced

**Theme:** Production hardening and advanced RAG techniques.

**Why:** Broader data ingestion expands use cases; RAGAS (Z) gives publishable evaluation metrics; Docker (W) makes it deployable anywhere; async (AA) handles real workloads.

### Checklist
- [ ] **V** — Web ingestion
- [ ] **W** — Docker
- [ ] **X** — Embedding model comparison
- [ ] **Y** — MLflow experiment tracking
- [ ] **Z** — RAGAS evaluation
- [ ] **AA** — Async pipeline
