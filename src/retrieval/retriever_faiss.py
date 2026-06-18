import logging
from typing import Any

import faiss
import numpy as np

from src.config import BASE
from src.embeddings.embed import Embedder
from src.ingestion.loader import load_documents
from src.chunking.chunk import chunk_documents
from src.retrieval._filter import filter_by_source, normalize_sources
from src.store.sqlite_store import ChunkStore
from src.utils.cache import cache_paths

logger = logging.getLogger(__name__)

# Cells probed per IVF query. Held fixed (the standard practice: tune nprobe to a recall target,
# not to nlist) so that with nlist ~ sqrt(N) the search cost stays ~sqrt(N) sublinear. A value
# that scales with nlist (e.g. nlist//10) would make IVF scan ~N/10 points, i.e. linear.
IVF_NPROBE = 16


class RetrieverFAISS:
    def __init__(
        self,
        chunked_docs: list[dict[str, str]],
        doc_embeddings: np.ndarray,
        index_type: str = "flat",
        embedder: Embedder | None = None,
        nprobe: int = IVF_NPROBE,
    ) -> None:
        """Build a FAISS index (flat or IVF) from chunk embeddings and store the docs.

        The embedder embeds the query string at retrieve time; optional so callers with
        raw query vectors (e.g. tests) can use _retrieve_vec. nprobe (IVF only) is the fixed
        number of cells searched per query.
        """
        self.docs = chunked_docs
        self.embedder = embedder
        vectors = doc_embeddings.astype("float32")
        faiss.normalize_L2(vectors)
        dim = vectors.shape[1]

        if index_type == "ivf":
            nlist = max(1, int(len(vectors) ** 0.5))
            quantizer = faiss.IndexFlatIP(dim)
            self.index = faiss.IndexIVFFlat(quantizer, dim, nlist, faiss.METRIC_INNER_PRODUCT)
            self.index.train(vectors)
            self.index.nprobe = min(nprobe, nlist)
        else:  # flat
            self.index = faiss.IndexFlatIP(dim)

        self.index.add(vectors)

    @classmethod
    def from_index(
        cls,
        chunked_docs: list[dict[str, str]],
        index: faiss.Index,
        embedder: Embedder | None = None,
    ) -> "RetrieverFAISS":
        """Construct a RetrieverFAISS from an already-loaded FAISS index, bypassing __init__."""
        obj = cls.__new__(cls)
        obj.docs = chunked_docs
        obj.index = index
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
            raise ValueError("RetrieverFAISS.retrieve needs an embedder; pass one to build, or call _retrieve_vec with a vector.")
        return self._retrieve_vec(self.embedder.embed_query(query), top_k=top_k, source=source)

    def _retrieve_vec(
        self,
        query_embedding: np.ndarray,
        top_k: int = BASE.top_k,
        source: str | list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Return the top_k chunks most similar to query_embedding using the FAISS index.

        FAISS has no payload filter, so when a source filter is set the search widens to the
        whole index and non-matching sources are dropped afterward (the awkward-without-Qdrant
        path); top_k is applied after filtering.
        """
        query = np.array(query_embedding, dtype="float32")
        if query.ndim == 1:
            query = query.reshape(1, -1)
        faiss.normalize_L2(query)
        search_k = self.index.ntotal if normalize_sources(source) is not None else top_k
        scores, indices = self.index.search(query, search_k)

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

        return filter_by_source(results, source)[:top_k]


def build_faiss_retriever(
    data_path: str,
    embedder: Embedder,
    index_type: str = "flat",
    chunk_max_tokens: int | None = None,
) -> RetrieverFAISS:
    """Build a FAISS retriever, loading index and chunks from cache if available."""
    effective_chunk_size = chunk_max_tokens or BASE.chunk_max_tokens
    paths = cache_paths(embedder.model_name, effective_chunk_size)
    chunk_store = ChunkStore(str(paths.sqlite_db))
    if paths.faiss_index.exists() and chunk_store.exists():
        logger.info("Loading from FAISS + SQLite cache...")
        chunked_docs = chunk_store.load()
        index = faiss.read_index(str(paths.faiss_index))
        return RetrieverFAISS.from_index(chunked_docs, index, embedder=embedder)
    docs = load_documents(data_path)
    chunked_docs = chunk_documents(docs, chunk_max_tokens=effective_chunk_size)
    doc_embeddings = embedder.embed_documents([d["text"] for d in chunked_docs])
    chunk_store.save(chunked_docs)
    retriever = RetrieverFAISS(chunked_docs, doc_embeddings, index_type=index_type, embedder=embedder)
    faiss.write_index(retriever.index, str(paths.faiss_index))
    logger.info("Embeddings saved to FAISS + SQLite cache.")
    return retriever
