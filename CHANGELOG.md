# Changelog

## v1.0 (2026-06-18)

First complete release of the from-scratch RAG pipeline.

### Pipeline
- Layout-aware PDF ingestion (pdfplumber: multi-column reading order, tables as Markdown), plus Markdown / text / DOCX.
- tiktoken sentence-aware chunking (128 tokens, 50 overlap); tables kept atomic.
- sentence-transformers embeddings (swappable model).
- Retrieval: numpy cosine, FAISS (flat / IVF), Qdrant, BM25, hybrid (RRF / weighted), cross-encoder rerank, HyDE, source filter.
- Generation: Ollama (local), OpenAI, or Groq (OpenAI-compatible, free tier).

### Serving
- FastAPI server: query, streaming, compare, evaluate, presets, sources.
- Streamlit dashboard: Query / Compare / Evaluate / Chat, with conversation memory.

### Evaluation
- Keyword + LLM-as-judge QA benchmark (29 pairs), tracked in MLflow.
- Synthetic scaling benchmark (numpy / FAISS / Qdrant: latency, memory, recall to N=500k; random and structured GloVe data).
- BEIR retrieval-quality eval (SciFact, NFCorpus) via pytrec_eval.

### Ops
- Docker (compose, plus a bundled-Ollama override), CI (GitHub Actions, pytest on 3.11/3.12), MIT license.
- Live deploy on Google Cloud Run (API + dashboard, Groq free tier, scale-to-zero).
