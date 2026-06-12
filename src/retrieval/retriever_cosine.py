import json
import logging
from typing import Any

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from src.config import BASE
from src.embeddings.embed import Embedder
from src.ingestion.loader import load_documents
from src.chunking.chunk import chunk_documents
from src.utils.cache import cache_paths

logger = logging.getLogger(__name__)


class RetrieverCosine:
    def __init__(
        self,
        chunked_docs: list[dict[str, str]],
        doc_embeddings: np.ndarray,
        embedder: Embedder | None = None,
    ) -> None:
        """Store chunk documents, their pre-computed embeddings, and the embedder.

        The embedder is used to embed the query string at retrieve time. It is optional
        so callers that already hold raw query vectors (e.g. tests) can use _retrieve_vec.
        """
        self.docs = chunked_docs
        self.embeddings = doc_embeddings
        self.embedder = embedder

    def retrieve(self, query: str, top_k: int = BASE.top_k) -> list[dict[str, Any]]:
        """Embed the query string and return the top_k most similar chunks."""
        if self.embedder is None:
            raise ValueError("RetrieverCosine.retrieve needs an embedder; pass one to build, or call _retrieve_vec with a vector.")
        return self._retrieve_vec(self.embedder.embed_query(query), top_k=top_k)

    def _retrieve_vec(self, query_embedding: np.ndarray, top_k: int = BASE.top_k) -> list[dict[str, Any]]:
        """Return the top_k chunks most similar to query_embedding by cosine similarity."""
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        results = []
        for i in top_indices:
            results.append({
                "text": self.docs[i]["text"],
                "source": self.docs[i]["source"],
                "score": float(similarities[i])
            })

        for r in results:
            logger.debug("%.4f | [%s] %s", r["score"], r["source"], r["text"])

        return results


def build_cosine_retriever(
    data_path: str,
    embedder: Embedder,
    chunk_max_tokens: int | None = None,
) -> RetrieverCosine:
    """Build a cosine similarity retriever, loading embeddings from numpy cache if available."""
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
    return RetrieverCosine(chunked_docs, doc_embeddings, embedder=embedder)
