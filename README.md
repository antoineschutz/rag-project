# RAG Pipeline

A from-scratch RAG (Retrieval-Augmented Generation) pipeline — no LangChain, no LlamaIndex. Built incrementally to understand each component of the RAG stack.

## Architecture

Data flows linearly through five stages:

1. **Ingestion** — loads PDFs from `./data/`
2. **Chunking** — sentence-aware splitting with tiktoken (`cl100k_base`), max 128 tokens per chunk, 50-token overlap
3. **Embedding** — `all-MiniLM-L6-v2` via `sentence-transformers`
4. **Retrieval** — FAISS vector index (exact `IndexFlatIP` or approximate `IndexIVFFlat`) backed by SQLite; sklearn cosine similarity kept as a comparison baseline via `--store numpy`
5. **Generation** — dispatches to Ollama (local) or OpenAI

## Setup

**Requirements:** Python 3.9+, and either [Ollama](https://ollama.com) running locally or an OpenAI API key.

```bash
git clone <repo-url>
cd rag-project

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

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

# See all options
python main.py --help
```

Place PDF files in `./data/` to include them in the knowledge base.

## Storage backends

| Flag | Index | Storage | Best for |
|------|-------|---------|---------|
| `--store numpy` (default) | sklearn cosine similarity | `.npy` + `.json` | Baseline comparison, small corpora |
| `--store faiss` | FAISS `IndexFlatIP` (exact) | `faiss.index` + SQLite | General use, supports incremental updates |
| `--store faiss --index-type ivf` | FAISS `IndexIVFFlat` (approximate) | `faiss.index` + SQLite | Large corpora (10k+ chunks) |

Cache files are stored in `./cache/`. Delete them to force a full re-embed on the next run.

## Experiment results

Queries grounded in `data/rag_lewis2020.pdf` (Lewis et al., 2020) — specific technical details a small LLM cannot reliably answer without retrieval. Model: `phi3` via Ollama. ✓ = correct, ~ = partially correct, ✗ = wrong or hallucinated.

| Query | Ground truth | No-RAG | RAG | Notes |
|---|---|---|---|---|
| `"What is the difference between RAG-Sequence and RAG-Token?"` | RAG-Sequence uses the same retrieved document for the entire output; RAG-Token can use a different document per output token | ✗ | ✓ | No-RAG confused "RAG" with immunology. RAG correctly distinguished same-doc-per-sequence vs different-doc-per-token |
| `"What exact match score did RAG-Sequence achieve on Natural Questions, and how does it compare to T5-11B?"` | **44.5% EM** vs. T5-11B's 34.5%, despite RAG having 626M trainable parameters vs. T5's 11B | ✗ | ✗ | No-RAG gave a vague non-answer. RAG retrieved the correct chunk but phi3 cited 28.9 as RAG's score — comparison reversed |
| `"What Wikipedia dump does RAG use as its non-parametric memory, and how many documents does it contain?"` | December 2018 Wikipedia dump, split into 100-word chunks → **~21 million documents** indexed with FAISS | ✗ | ✓ | No-RAG hallucinated "WikiText1, ~1B tokens". RAG correctly cited December 2018 dump, 100-word chunks, 21M docs |
| `"How does RAG update its knowledge about the world without retraining the model?"` | By hot-swapping the document index; a mismatched index (2018 index for 2016 world leaders) dropped accuracy from 70% to 4% | ✗ | ✓ | No-RAG described continual learning/fine-tuning. RAG correctly cited index hot-swapping with 70% → 4% accuracy |
| `"Why is the document encoder kept frozen during RAG training?"` | Updating it would require rebuilding the full FAISS index over 21M documents after every gradient step — only the query encoder and BART generator are fine-tuned | ✗ | ✗ | No-RAG gave generic rationale. RAG retrieved the right chunk but phi3 concluded "the text does not provide a specific reason" — generation failure |

**RAG score: 3 / 5**
