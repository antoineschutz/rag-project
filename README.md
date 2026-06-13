# RAG Pipeline

A from-scratch RAG (Retrieval-Augmented Generation) pipeline: no LangChain, no LlamaIndex. Built incrementally to understand each component of the RAG stack.

## Architecture

Data flows linearly through five stages:

1. **Ingestion**: layout-aware extraction with `pdfplumber` (multi-column reading order; tables, including borderless/booktabs tables, rendered as Markdown), plus Markdown, text, and DOCX, from `./data/`
2. **Chunking**: sentence-aware splitting with tiktoken (`cl100k_base`), max 128 tokens / 50-token overlap. Tables are kept atomic (never split mid-row) and bundled with surrounding prose when they fit
3. **Embedding**: `sentence-transformers`, model swappable via `--embed-model` (`all-MiniLM-L6-v2` default; `bge-*`, `e5-*` supported)
4. **Retrieval**: dense cosine (numpy or FAISS), BM25 lexical, or hybrid fusion. Optional cross-encoder re-ranking and HyDE query expansion on top
5. **Generation**: Ollama (local) or OpenAI, with a configurable context window (`num_ctx`)

## Setup

**Requirements:** Python 3.10+, and either [Ollama](https://ollama.com) running locally or an OpenAI API key.

```bash
git clone https://github.com/antoineschutz/rag-project.git
cd rag-project

python -m venv venv
source venv/bin/activate 

pip install -r requirements.txt

# Ollama backend (default)
ollama pull phi3

# OpenAI backend: copy .env.example to .env and set OPENAI_API_KEY
```

## Usage

```bash
source venv/bin/activate

# Ask a question (defaults: dense RAG, Ollama, numpy store)
python main.py --query "What is the difference between RAG-Sequence and RAG-Token?"

# Skip retrieval: query the LLM directly with no context
python main.py --query "..." --no-rag

# OpenAI instead of Ollama (needs OPENAI_API_KEY)
python main.py --query "..." --backend gpt

# Retrieval method: BM25 lexical (no embeddings), or hybrid (dense + BM25 fused)
python main.py --query "..." --retriever bm25
python main.py --query "..." --retriever hybrid --fusion weighted --alpha 0.7   # default fusion is rrf

# Cross-encoder re-ranking, stacks on top of any retriever
python main.py --query "..." --rerank

# HyDE: draft a hypothetical answer first and embed that instead of the raw query
python main.py --query "..." --hyde

# Bigger context window (for high top_k / large chunks; phi3 supports up to 131072)
python main.py --query "..." --num-ctx 8192

# Dense store: numpy cosine (default), FAISS IndexFlatIP (exact, incremental updates),
# or FAISS IndexIVFFlat (approximate, for large 10k+ corpora)
python main.py --query "..." --store faiss
python main.py --query "..." --store faiss --index-type ivf

# Swap the embedding model
python main.py --query "..." --embed-model BAAI/bge-small-en-v1.5

# See all options
python main.py --help
```

Drop PDF, Markdown, text, or DOCX files in `./data/` to add them to the knowledge base. Embeddings and chunk text are cached in `./cache/`. Delete it to force a full re-embed.

## API server

A FastAPI server (`src/api/server.py`) exposes the same pipeline over HTTP:

```bash
uvicorn src.api.server:app --reload
```

Interactive docs (Swagger UI) live at `http://127.0.0.1:8000/docs`. On startup the server warms the presets it will serve (loads the embedder, index, and reranker) so the first request is not cold.

| endpoint | purpose |
|----------|---------|
| `GET /health` | liveness check |
| `GET /presets` | list the named presets (`baseline`, `best`, `no-rag`) and their configs |
| `POST /query` | answer one question; returns the answer plus the retrieved chunks. Select the pipeline with a preset name, inline knob overrides, or omit `config` for the best preset |
| `POST /evaluate` | score a config over the keyword-graded QA set (`accuracy_29`, optional LLM judge). A known preset `name` wins; pass an inline `config` under a non-preset name to score a custom config |
| `POST /compare` | run one query through two configs and return both answers and chunks side by side |

## Dashboard

A Streamlit dashboard (`dashboard/`) provides a browser UI over the API. It is presentation only: every page calls the FastAPI server, so the pipeline stays decoupled from the UI. Run both processes from the repo root:

```bash
uvicorn src.api.server:app --reload   # terminal 1: the API
streamlit run dashboard/Home.py       # terminal 2: the UI (opens http://localhost:8501)
```

Four pages:

- **Query**: ask one question, see the answer and the retrieved chunks; pick a preset or send inline overrides.
- **Compare**: run one question through two configs (e.g. baseline vs no-RAG) side by side.
- **Evaluate**: chart the benchmark runs logged in MLflow, or trigger a live evaluation over the QA set.
- **Chat**: multi-turn conversation; follow-up questions are condensed into a standalone query against the history before retrieval.

Set `RAG_API_URL` if the API runs somewhere other than `http://127.0.0.1:8000`.

## Results

Benchmarked on 32 hand-written Q/A pairs (8 difficulty levels) over a corpus of real ML papers plus a few synthetic docs (`phi3`, local). Two qualitative sweep rounds, then a scored benchmark tracked in MLflow:

- **`eval_results/` (round 1)** exposed a table-extraction bug: borderless / booktabs tables weren't parsed, so every table-lookup question failed. Fixed in ingestion and chunking.
- **`eval_results2/` (round 2, 7 dimensions, post-fix)** showed the real ceiling is phi3's context window, not retrieval. At `top_k ≥ 40` or chunks ≥ 256 the prompt overflows the 4096 default and the model returns truncated gibberish.

`scripts/benchmark.py` scores every answer two ways: an exact-match keyword check (`accuracy_29`) and an independent LLM-as-judge (`gpt-4o-mini`, not the model under test). Retrieval helps, and tuning helps more:

| config | exact match | LLM judge |
|--------|-------------|-----------|
| no-RAG (phi3 alone) | 5/29 (17%) | 4/29 (14%) |
| default RAG (dense, MiniLM, k=15) | 14/29 (48%) | 13/29 (45%) |
| best (hybrid+RRF, rerank, bge-small, k=20) | 17/29 (59%) | 14/29 (48%) |

The judge is stricter and narrows the gap (it catches keyword false positives), but agrees on the ranking. Cross-document synthesis and deep-table lookups stay unsolved by single-shot retrieval.

Full per-question breakdown: [`eval_results2/summary.md`](eval_results2/summary.md). Reproduce: `python scripts/benchmark.py --config best --judge`, then `mlflow ui` to browse runs.
