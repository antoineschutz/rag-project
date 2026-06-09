# RAG Pipeline

A from-scratch RAG (Retrieval-Augmented Generation) pipeline — no LangChain, no LlamaIndex. Built incrementally to understand each component of the RAG stack.

## Architecture

Data flows linearly through five stages:

1. **Ingestion** — loads PDFs, Markdown, and DOCX files from `./data/`
2. **Chunking** — sentence-aware splitting with tiktoken (`cl100k_base`), max 128 tokens per chunk, 50-token overlap
3. **Embedding** — `all-MiniLM-L6-v2` via `sentence-transformers`
4. **Retrieval** — dense cosine (numpy or FAISS), BM25 lexical search, or hybrid fusion of both; optional cross-encoder re-ranking on top
5. **Generation** — dispatches to Ollama (local) or OpenAI

## Setup

**Requirements:** Python 3.9+, and either [Ollama](https://ollama.com) running locally or an OpenAI API key.

```bash
git clone git@github.com:antoineschutz/rag-project.git
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

# Ask a question (RAG path)
python main.py --query "What is the difference between RAG-Sequence and RAG-Token?"

# Skip retrieval — query the LLM directly with no context
python main.py --query "..." --no-rag

# Use OpenAI instead of Ollama
python main.py --query "..." --backend gpt

# Use FAISS + SQLite backend (default: numpy)
python main.py --query "..." --store faiss

# Use approximate IVF index (better for large corpora)
python main.py --query "..." --store faiss --index-type ivf

# BM25 (lexical) retrieval
python main.py --query "..." --retriever bm25

# Hybrid retrieval (dense + BM25, RRF fusion)
python main.py --query "..." --retriever hybrid

# Hybrid with weighted-sum fusion and custom alpha
python main.py --query "..." --retriever hybrid --fusion weighted --alpha 0.7

# Cross-encoder re-ranking on top of any retriever
python main.py --query "..." --rerank

# See all options
python main.py --help
```

Place PDF, Markdown, or DOCX files in `./data/` to include them in the knowledge base.

## Storage backends

| Flag | Index | Storage | Best for |
|------|-------|---------|---------|
| `--store numpy` (default) | sklearn cosine similarity | `.npy` + `.json` | Baseline comparison, small corpora |
| `--store faiss` | FAISS `IndexFlatIP` (exact) | `faiss.index` + SQLite | General use, supports incremental updates |
| `--store faiss --index-type ivf` | FAISS `IndexIVFFlat` (approximate) | `faiss.index` + SQLite | Large corpora (10k+ chunks) |

Cache files are stored in `./cache/`. Delete them to force a full re-embed on the next run.

## Retrieval modes

| Flag | Method | Notes |
|------|--------|-------|
| (default) | Dense cosine | Uses `--store` backend above |
| `--retriever bm25` | BM25 lexical | No embeddings needed |
| `--retriever hybrid` | Dense + BM25 fused | `--fusion rrf\|weighted`, `--alpha` controls weight (default 0.5) |
| `--rerank` | Cross-encoder re-score | Stacks on top of any retriever |

## Experiment results

Model: `phi3` via Ollama. ✓ = correct, ~ = partially correct, ✗ = wrong or hallucinated.

Note: `rag_design_notes.md` and `qa_benchmark_report.docx` are synthetic documents created for this project.

| Query | Ground truth | Source | Difficulty | No-RAG | Dense RAG | Best combo | Notes |
|---|---|---|---|---|---|---|---|
| `"How much did adding source attribution to the RAG prompt reduce hallucination?"` | From 23% to 6% | `rag_design_notes.md` | Flat Markdown file — no parsing challenge | ✗ | ✓ | — | RAG retrieves the unique stat cleanly |
| `"What two pre-training tasks does BERT use?"` | MLM and NSP | `bert_devlin2018.pdf` | PDF prose — two-column reading order | ✓ | ✗ | ✓ `--retriever hybrid --rerank` | Dense drifted to GPT-paper chunks; BM25 locked on "BERT", reranker filtered noise |
| `"What is the query latency of IndexFlatIP compared to IndexIVF?"` | FlatIP: 4 ms · IVF: 1 ms | `rag_design_notes.md` | Markdown table — exact numeric retrieval | ✗ | ~ | ✓ `--retriever bm25 --rerank` | Dense got direction right but wrong numbers; BM25 exact-matched the rare technical terms |
| `"How many more attention heads does BERT-BASE have compared to the base Transformer model?"` | 12 − 8 = 4 | `bert_devlin2018.pdf` + `attention_is_all_you_need.pdf` | Cross-document synthesis — two papers | ✗ | ✗ | ✗ `--retriever hybrid --top-k 10 --rerank` | No single-shot retrieval strategy surfaces both facts together; requires multi-hop query decomposition |

**Key findings:**
- Single-document retrieval (Q1, Q2, Q3) is fully solvable with the right retriever combination
- BM25 outperforms dense on queries with rare exact-match terminology
- Cross-document synthesis (Q4) remains unsolved — a structural limitation of single-shot retrieval

---

### HyDE comparison (`--hyde`)

HyDE (Hypothetical Document Embeddings) asks the LLM to draft a hypothetical answer passage before retrieval, then embeds that passage instead of the raw query. This closes the vocabulary gap between layperson queries and technical document language.

Model: `llama3.1` (8B). Query: *"What trick does the Transformer use so it doesn't have to read sentences left to right?"*

| Path | Answer | Notes |
|---|---|---|
| No-RAG | ✓ | llama3.1 knows self-attention from training data |
| Dense RAG | ~ | Retrieved BERT MLM chunks — right idea, wrong paper |
| Dense RAG + HyDE | ~ | Retrieved cross-attention chunks — vague |
| `--hyde --retriever hybrid --rerank` | ✗ | Still retrieves BERT MLM; query semantics map to bidirectionality regardless of retriever |

The query's phrasing ("doesn't have to read left to right") maps to BERT's bidirectionality story in embedding space across all retriever strategies tried. No-RAG remains the best path for this query — llama3.1 answers correctly from training data without retrieval.
