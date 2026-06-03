import json
import logging
import os

import faiss
import numpy as np

from src.config import config
from src.embeddings.embed import Embedder
from src.ingestion.loader import load_pdfs
from src.chunking.chunk import chunk_documents
from src.retrieval.retriever import Retriever
from src.retrieval.retriever_faiss import RetrieverFAISS
from src.store.sqlite_store import ChunkStore

logger = logging.getLogger(__name__)


def build_retriever(
    store: str,
    data_path: str,
    embedder: Embedder,
    index_type: str = "flat",
) -> Retriever | RetrieverFAISS:
    os.makedirs(config.CACHE_DIR, exist_ok=True)

    if store == "numpy":
        if os.path.exists(config.EMBEDDINGS_PATH) and os.path.exists(config.CHUNKS_PATH):
            logger.info("Loading from numpy cache...")
            with open(config.CHUNKS_PATH) as f:
                chunked_docs = json.load(f)
            doc_embeddings = np.load(config.EMBEDDINGS_PATH)
        else:
            docs = load_pdfs(data_path)
            chunked_docs = chunk_documents(docs)
            doc_embeddings = embedder.embed_documents([d["text"] for d in chunked_docs])
            np.save(config.EMBEDDINGS_PATH, doc_embeddings)
            with open(config.CHUNKS_PATH, "w") as f:
                json.dump(chunked_docs, f, indent=4)
            logger.info("Embeddings saved to numpy cache.")
        return Retriever(chunked_docs, doc_embeddings)

    else:  # faiss
        chunk_store = ChunkStore(config.SQLITE_DB_PATH)
        if os.path.exists(config.FAISS_INDEX_PATH) and chunk_store.exists():
            logger.info("Loading from FAISS + SQLite cache...")
            chunked_docs = chunk_store.load()
            index = faiss.read_index(config.FAISS_INDEX_PATH)
            return RetrieverFAISS.from_index(chunked_docs, index)
        else:
            docs = load_pdfs(data_path)
            chunked_docs = chunk_documents(docs)
            doc_embeddings = embedder.embed_documents([d["text"] for d in chunked_docs])
            chunk_store.save(chunked_docs)
            retriever = RetrieverFAISS(chunked_docs, doc_embeddings, index_type=index_type)
            faiss.write_index(retriever.index, config.FAISS_INDEX_PATH)
            logger.info("Embeddings saved to FAISS + SQLite cache.")
            return retriever
