# RAG Pipeline for Scientific Papers

A from-scratch RAG (Retrieval-Augmented Generation) pipeline: no LangChain, no LlamaIndex. Built incrementally to understand each component of the RAG stack.

The pipeline is tuned for scientific and research PDFs (the working corpus is ML papers). The ingestion heuristics in particular target academic layouts: two-column reflow, booktabs and borderless numeric results tables, "Table N" captions, and scientific-notation repair. Plain prose, Markdown, text, and DOCX are handled generically, but other document types (invoices, contracts, brochures) will extract as readable text without the specialized table reconstruction and fact verbalization.

## Architecture

Data flows linearly through five stages:

1. **Ingestion**: layout-aware extraction with `pdfplumber` (multi-column reading order; tables, including borderless/booktabs tables, rendered as Markdown), plus Markdown, text, and DOCX, from `./data/`
2. **Chunking**: sentence-aware splitting with tiktoken (`cl100k_base`), max 128 tokens / 50-token overlap. Tables are kept atomic (never split mid-row) and bundled with surrounding prose when they fit
3. **Embedding**: `sentence-transformers`, model swappable via `--embed-model` (`all-MiniLM-L6-v2` default; `bge-*`, `e5-*` supported)
4. **Retrieval**: dense (numpy cosine, FAISS, or Qdrant), BM25 lexical, or hybrid fusion. Optional cross-encoder re-ranking and HyDE query expansion on top, plus an optional source filter to restrict retrieval to chosen documents
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

# Qdrant store: in-process by default (rebuilt from the embedding cache). Set QDRANT_URL to
# use a persistent server, which reuses an existing collection instead of re-upserting.
python main.py --query "..." --store qdrant
QDRANT_URL=http://localhost:6333 python main.py --query "..." --store qdrant

# Restrict retrieval to specific documents (source filter; works with any store/retriever)
python main.py --query "..." --source rag_lewis2020.pdf realm_guu2020.pdf

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
| `GET /sources` | list the document filenames in the data dir, for the source filter |
| `POST /query` | answer one question; returns the answer plus the retrieved chunks. Select the pipeline with a preset name, inline knob overrides (including `store` and `source`), or omit `config` for the best preset |
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

Benchmarked on 29 hand-written Q/A pairs (8 difficulty levels) over a corpus of real ML papers plus a few synthetic docs. `scripts/benchmark.py` scores every answer two ways: an exact-match keyword check (`accuracy_29`) and an LLM-as-judge (`gpt-4o-mini`). The goal is lifting a small local model (`phi3`) with retrieval; the hosted models (OpenAI, Groq) are ceiling probes.

| config | exact match | LLM judge |
|--------|-------------|-----------|
| phi3, no-RAG | 5/29 (17%) | 3/29 (10%) |
| phi3, baseline RAG (dense MiniLM, k=15) | 17/29 (59%) | 14/29 (48%) |
| phi3, best RAG (hybrid+RRF, rerank, bge-small, k=20) | 19/29 (66%) | 15/29 (52%) |
| GPT-4o-mini, no-RAG | 8/29 (28%) | 8/29 (28%) |
| GPT-4o-mini, RAG | 27/29 (93%) | 24/29 (83%) |
| Llama-3.1-8B, no-RAG | 5/29 (17%) | 4/29 (14%) |
| Llama-3.1-8B, RAG | 27/29 (93%) | 25/29 (86%) |

Retrieval does the heavy lifting: RAG takes phi3 from 10% to 52% on the judge, and even the hosted models gain roughly 55 points with retrieval (they cannot answer this corpus from parametric knowledge alone). The judge is stricter than the keyword check (it catches substring false positives) but agrees on the ranking. The `gpt` preset and the judge are both gpt-4o-mini, so that row is self-graded.

Reproduce: `python scripts/benchmark.py --config best --judge`, then `mlflow ui` to browse runs.
