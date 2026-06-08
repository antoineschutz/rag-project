import json
import logging
import os
from typing import Any

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from src.config import config
from src.embeddings.embed import Embedder
from src.ingestion.loader import load_documents
from src.chunking.chunk import chunk_documents

logger = logging.getLogger(__name__)


class RetrieverCosine:
    def __init__(self, chunked_docs: list[dict[str, str]], doc_embeddings: np.ndarray) -> None:
        """Store chunk documents and their pre-computed embeddings."""
        self.docs = chunked_docs
        self.embeddings = doc_embeddings

    def retrieve(self, query_embedding: np.ndarray, top_k: int = config.TOP_K) -> list[dict[str, Any]]:
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


def build_cosine_retriever(data_path: str, embedder: Embedder) -> RetrieverCosine:
    """Build a cosine similarity retriever, loading embeddings from numpy cache if available."""
    os.makedirs(config.CACHE_DIR, exist_ok=True)
    if os.path.exists(config.EMBEDDINGS_PATH) and os.path.exists(config.CHUNKS_PATH):
        logger.info("Loading from numpy cache...")
        with open(config.CHUNKS_PATH) as f:
            chunked_docs = json.load(f)
        doc_embeddings = np.load(config.EMBEDDINGS_PATH)
    else:
        docs = load_documents(data_path)
        chunked_docs = chunk_documents(docs)
        doc_embeddings = embedder.embed_documents([d["text"] for d in chunked_docs])
        np.save(config.EMBEDDINGS_PATH, doc_embeddings)
        with open(config.CHUNKS_PATH, "w") as f:
            json.dump(chunked_docs, f, indent=4, ensure_ascii=False)
        logger.info("Embeddings saved to numpy cache.")
    return RetrieverCosine(chunked_docs, doc_embeddings)
