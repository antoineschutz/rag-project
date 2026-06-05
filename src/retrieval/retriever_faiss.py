import logging
from typing import Any

import faiss
import numpy as np

from src.config import config

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
            results.append({
                "text": self.docs[idx]["text"],
                "source": self.docs[idx]["source"],
                "score": float(score),
            })
            logger.debug("%.4f | [%s] %s", score, self.docs[idx]["source"], self.docs[idx]["text"])

        return results
