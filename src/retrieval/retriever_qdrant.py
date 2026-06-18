import logging
from typing import Any

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchAny,
    PointStruct,
    VectorParams,
)

from src.config import BASE, env
from src.embeddings.embed import Embedder
from src.retrieval._dense_cache import load_or_build_chunk_embeddings
from src.retrieval._filter import normalize_sources

logger = logging.getLogger(__name__)


class RetrieverQdrant:
    """Dense retriever backed by a Qdrant collection (vectors + text/source payload)."""

    def __init__(
        self,
        chunked_docs: list[dict[str, str]],
        doc_embeddings: np.ndarray,
        embedder: Embedder | None = None,
        client: QdrantClient | None = None,
        collection: str = "chunks",
    ) -> None:
        """Create (or recreate) the collection and upsert one point per chunk.

        The embedder embeds the query string at retrieve time; optional so callers with raw
        query vectors (e.g. tests) can use _retrieve_vec. `client` defaults to an in-process
        ":memory:" instance; pass a server client to persist. Distance.COSINE so Qdrant
        normalizes internally (higher score = better, matching faiss/cosine semantics).
        """
        self.embedder = embedder
        self.collection = collection
        self.client = client or QdrantClient(":memory:")
        dim = doc_embeddings.shape[1]
        if self.client.collection_exists(collection):
            self.client.delete_collection(collection)
        self.client.create_collection(
            collection, vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
        )
        # Upsert in batches: a single request for the whole corpus exceeds Qdrant's payload
        # limit (~32 MB) at a few tens of thousands of vectors.
        batch_size = 1000
        for start in range(0, len(chunked_docs), batch_size):
            self.client.upsert(
                collection,
                points=[
                    PointStruct(
                        id=i,
                        vector=doc_embeddings[i].tolist(),
                        payload={"text": chunked_docs[i]["text"], "source": chunked_docs[i]["source"]},
                    )
                    for i in range(start, min(start + batch_size, len(chunked_docs)))
                ],
            )

    @classmethod
    def from_collection(
        cls,
        client: QdrantClient,
        collection: str = "chunks",
        embedder: Embedder | None = None,
    ) -> "RetrieverQdrant":
        """Wrap an already-populated collection, bypassing __init__ (no re-upsert).

        The text/source payload lives in the collection, so no local docs list is needed.
        """
        obj = cls.__new__(cls)
        obj.client = client
        obj.collection = collection
        obj.embedder = embedder
        return obj

    def retrieve(
        self,
        query: str,
        top_k: int = BASE.top_k,
        source: str | list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Embed the query string and return the top_k most similar chunks."""
        if self.embedder is None:
            raise ValueError("RetrieverQdrant.retrieve needs an embedder; pass one to build, or call _retrieve_vec with a vector.")
        return self._retrieve_vec(self.embedder.embed_query(query), top_k=top_k, source=source)

    def _retrieve_vec(
        self,
        query_embedding: np.ndarray,
        top_k: int = BASE.top_k,
        source: str | list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Return the top_k chunks most similar to query_embedding, optionally source-filtered."""
        vec = np.asarray(query_embedding, dtype="float32")
        if vec.ndim == 2:  # Embedder.embed_query returns (1, dim)
            vec = vec[0]

        allowed = normalize_sources(source)
        query_filter = None
        if allowed is not None:
            query_filter = Filter(
                must=[FieldCondition(key="source", match=MatchAny(any=sorted(allowed)))]
            )

        response = self.client.query_points(
            self.collection,
            query=vec.tolist(),
            limit=top_k,
            query_filter=query_filter,
            with_payload=True,
        )
        results = []
        for p in response.points:
            results.append({
                "text": p.payload["text"],
                "source": p.payload["source"],
                "score": float(p.score),
            })
            logger.debug("%.4f | [%s] %s", p.score, p.payload["source"], p.payload["text"])
        return results


def build_qdrant_retriever(
    data_path: str,
    embedder: Embedder,
    chunk_max_tokens: int | None = None,
    collection: str = "chunks",
) -> RetrieverQdrant:
    """Build a Qdrant retriever.

    With env.QDRANT_URL set, connect to that server and reuse an already-populated collection
    instead of re-upserting (so repeat runs are instant and use the server's HNSW). Otherwise
    run in-process (":memory:"), rebuilt from the shared numpy cache.
    """
    if env.QDRANT_URL:
        client = QdrantClient(url=env.QDRANT_URL)
        if client.collection_exists(collection):
            logger.info("Reusing existing Qdrant collection %r at %s", collection, env.QDRANT_URL)
            return RetrieverQdrant.from_collection(client, collection, embedder=embedder)
        chunked_docs, doc_embeddings = load_or_build_chunk_embeddings(data_path, embedder, chunk_max_tokens)
        return RetrieverQdrant(chunked_docs, doc_embeddings, embedder=embedder, client=client, collection=collection)

    chunked_docs, doc_embeddings = load_or_build_chunk_embeddings(data_path, embedder, chunk_max_tokens)
    return RetrieverQdrant(chunked_docs, doc_embeddings, embedder=embedder, collection=collection)
