"""Shared embedding-cache load-or-build for dense retrievers.

The numpy cosine and Qdrant backends share the same on-disk cache (`embeddings.npy` +
`chunks.json`, keyed by model + chunk size), so the chunk/embed step lives here once.
Kept out of `src/utils/cache.py` (path-layout only) so the ingestion/chunking imports do
not create a cycle.
"""

import json
import logging

import numpy as np

from src.config import BASE
from src.chunking.chunk import chunk_documents
from src.embeddings.embed import Embedder
from src.ingestion.loader import load_documents
from src.utils.cache import cache_paths

logger = logging.getLogger(__name__)


def load_or_build_chunk_embeddings(
    data_path: str,
    embedder: Embedder,
    chunk_max_tokens: int | None = None,
) -> tuple[list[dict[str, str]], np.ndarray]:
    """Return (chunked_docs, doc_embeddings), loading from the numpy cache or building it.

    Cache identity is the embedding model and chunk size (see `cache_paths`); the numpy and
    Qdrant dense backends reuse the same files.
    """
    effective_chunk_size = chunk_max_tokens or BASE.chunk_max_tokens
    paths = cache_paths(embedder.model_name, effective_chunk_size)
    if paths.embeddings.exists() and paths.chunks.exists():
        logger.info("Loading from numpy cache...")
        with open(paths.chunks) as f:
            chunked_docs = json.load(f)
        doc_embeddings = np.load(paths.embeddings)
    else:
        docs = load_documents(data_path)
        chunked_docs = chunk_documents(docs, chunk_max_tokens=effective_chunk_size)
        doc_embeddings = embedder.embed_documents([d["text"] for d in chunked_docs])
        np.save(paths.embeddings, doc_embeddings)
        with open(paths.chunks, "w") as f:
            json.dump(chunked_docs, f, indent=4, ensure_ascii=False)
        logger.info("Embeddings saved to numpy cache.")
    return chunked_docs, doc_embeddings
