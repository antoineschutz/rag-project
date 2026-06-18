# Shared image for both the API (uvicorn) and the dashboard (streamlit); the compose file
# picks the command per service.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# libgomp1 is the OpenMP runtime that faiss-cpu (and torch) need; slim does not ship it.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install the CPU-only torch wheel before the rest so we don't pull the multi-GB CUDA build
# that sentence-transformers would otherwise drag in.
COPY requirements.txt .
RUN pip install --extra-index-url https://download.pytorch.org/whl/cpu torch \
    && pip install -r requirements.txt

# Bake the NLTK and tiktoken data so containers need no network for chunking at runtime.
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')" \
    && python -c "import tiktoken; tiktoken.get_encoding('cl100k_base')"

# Bake the embedding/reranker models the warmed presets load, so a Cloud Run cold start needs no
# network: all-MiniLM (baseline), bge-small (best), ms-marco cross-encoder (reranker).
RUN python -c "from sentence_transformers import SentenceTransformer, CrossEncoder; \
SentenceTransformer('all-MiniLM-L6-v2'); \
SentenceTransformer('BAAI/bge-small-en-v1.5'); \
CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')"

# App code (data/ ships as a default corpus; a bind mount can override it).
COPY . .

# Bake the embedding/chunk cache for the baseline + best presets so startup loads it instead of
# embedding the corpus (faster cold start, and no runtime write to a read-mostly cloud filesystem).
RUN python -c "from src.config import PRESETS, IndexParams, as_config_dict; \
from src.retrieval.factory import build_index; \
[build_index(IndexParams.from_dict(as_config_dict(PRESETS[p]))) for p in ('baseline', 'best')]"

EXPOSE 8000 8501

# Default to the API; listen on Cloud Run's $PORT when set (8000 locally). Shell form so $PORT
# expands; the compose services and the cloud dashboard override this command.
CMD uvicorn src.api.server:app --host 0.0.0.0 --port ${PORT:-8000}
