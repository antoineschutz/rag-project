import logging
import os
from typing import Any

import faiss
import numpy as np

from src.config import config
from src.embeddings.embed import Embedder
from src.ingestion.loader import load_documents
from src.chunking.chunk import chunk_documents
from src.store.sqlite_store import ChunkStore
from src.retrieval.cache_utils import cache_matches, clear_cache, write_cache_model

logger = logging.getLogger(__name__)


class RetrieverFAISS:
    def __init__(
        self,
        chunked_docs: list[dict[str, str]],
        doc_embeddings: np.ndarray,
        index_type: str = "flat",
    ) -> None:
        """Build a FAISS index (flat or IVF) from chunk embeddings and store the docs."""
        self.docs = chunked_docs
        vectors = doc_embeddings.astype("float32")
        faiss.normalize_L2(vectors)
        dim = vectors.shape[1]

        if index_type == "ivf":
            nlist = max(1, int(len(vectors) ** 0.5))
            quantizer = faiss.IndexFlatIP(dim)
            self.index = faiss.IndexIVFFlat(quantizer, dim, nlist, faiss.METRIC_INNER_PRODUCT)
            self.index.train(vectors)
            self.index.nprobe = max(1, nlist // 10)
        else:  # flat
            self.index = faiss.IndexFlatIP(dim)

        self.index.add(vectors)

    @classmethod
    def from_index(cls, chunked_docs: list[dict[str, str]], index: faiss.Index) -> "RetrieverFAISS":
        """Construct a RetrieverFAISS from an already-loaded FAISS index, bypassing __init__."""
        obj = cls.__new__(cls)
        obj.docs = chunked_docs
        obj.index = index
        return obj

    def retrieve(self, query_embedding: np.ndarray, top_k: int = config.TOP_K) -> list[dict[str, Any]]:
        """Return the top_k chunks most similar to query_embedding using the FAISS index."""
        query = np.array(query_embedding, dtype="float32")
        if query.ndim == 1:
            query = query.reshape(1, -1)
        faiss.normalize_L2(query)
        scores, indices = self.index.search(query, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            results.append({
                "text": self.docs[idx]["text"],
                "source": self.docs[idx]["source"],
                "score": float(score),
            })
            logger.debug("%.4f | [%s] %s", score, self.docs[idx]["source"], self.docs[idx]["text"])

        return results


def build_faiss_retriever(
    data_path: str,
    embedder: Embedder,
    index_type: str = "flat",
    chunk_max_tokens: int | None = None,
) -> RetrieverFAISS:
    """Build a FAISS retriever, loading index and chunks from cache if available."""
    effective_chunk_size = chunk_max_tokens or config.CHUNK_MAX_TOKENS
    stamp = f"{embedder.model_name}:{effective_chunk_size}"
    os.makedirs(config.CACHE_DIR, exist_ok=True)
    if not cache_matches(stamp):
        logger.info("Cache stamp changed — clearing cache.")
        clear_cache()
    chunk_store = ChunkStore(config.SQLITE_DB_PATH)
    if os.path.exists(config.FAISS_INDEX_PATH) and chunk_store.exists():
        logger.info("Loading from FAISS + SQLite cache...")
        chunked_docs = chunk_store.load()
        index = faiss.read_index(config.FAISS_INDEX_PATH)
        return RetrieverFAISS.from_index(chunked_docs, index)
    docs = load_documents(data_path)
    chunked_docs = chunk_documents(docs, chunk_max_tokens=effective_chunk_size)
    doc_embeddings = embedder.embed_documents([d["text"] for d in chunked_docs])
    chunk_store.save(chunked_docs)
    retriever = RetrieverFAISS(chunked_docs, doc_embeddings, index_type=index_type)
    faiss.write_index(retriever.index, config.FAISS_INDEX_PATH)
    write_cache_model(stamp)
    logger.info("Embeddings saved to FAISS + SQLite cache.")
    return retriever
