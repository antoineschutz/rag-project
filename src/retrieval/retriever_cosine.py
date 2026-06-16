import logging
from typing import Any

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from src.config import BASE
from src.embeddings.embed import Embedder
from src.retrieval._dense_cache import load_or_build_chunk_embeddings
from src.retrieval._filter import normalize_sources

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

    def retrieve(
        self,
        query: str,
        top_k: int = BASE.top_k,
        source: str | list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Embed the query string and return the top_k most similar chunks."""
        if self.embedder is None:
            raise ValueError("RetrieverCosine.retrieve needs an embedder; pass one to build, or call _retrieve_vec with a vector.")
        return self._retrieve_vec(self.embedder.embed_query(query), top_k=top_k, source=source)

    def _retrieve_vec(
        self,
        query_embedding: np.ndarray,
        top_k: int = BASE.top_k,
        source: str | list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Return the top_k chunks most similar to query_embedding by cosine similarity.

        An optional source filter masks the candidate indices before taking top_k, so the
        ranking is computed over only the allowed documents.
        """
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        ranked = np.argsort(similarities)[::-1]
        allowed = normalize_sources(source)
        if allowed is not None:
            ranked = [i for i in ranked if self.docs[i]["source"] in allowed]
        top_indices = ranked[:top_k]

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
    chunked_docs, doc_embeddings = load_or_build_chunk_embeddings(data_path, embedder, chunk_max_tokens)
    return RetrieverCosine(chunked_docs, doc_embeddings, embedder=embedder)
