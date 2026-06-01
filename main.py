import argparse
import json
import logging
import os

import numpy as np

from src.config import config
from src.ingestion.loader import load_pdfs
from src.chunking.chunk import chunk_documents
from src.embeddings.embed import Embedder
from src.retrieval.retriever import Retriever
from src.retrieval.retriever_faiss import RetrieverFAISS
from src.store.sqlite_store import ChunkStore
from src.prompts.templates import build_prompt_rag, build_prompt_no_rag
from src.llm.client import LLMClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the RAG pipeline.")
    parser.add_argument("--query", required=True, help="Question to ask the model")
    parser.add_argument("--data-path", default=None, help="Path to PDF data directory")
    parser.add_argument("--backend", choices=["ollama", "gpt"], default=None, help="LLM backend")
    parser.add_argument("--model", default=None, help="Model name override")
    parser.add_argument("--top-k", type=int, default=None, dest="top_k", help="Number of chunks to retrieve")
    parser.add_argument("--no-rag", action="store_true", help="Skip retrieval; query LLM directly")
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging verbosity (default: INFO)",
    )
    parser.add_argument(
        "--store",
        choices=["numpy", "faiss"],
        default="numpy",
        help="Storage and retrieval backend (default: numpy)",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s — %(message)s")
    for name in ("__main__", "src"):
        logging.getLogger(name).setLevel(args.log_level)

    backend = args.backend or config.LLM_BACKEND
    top_k = args.top_k or config.TOP_K
    data_path = args.data_path or config.DATA_PATH

    llm = LLMClient(backend=backend, model=args.model)

    if args.no_rag:
        prompt = build_prompt_no_rag(args.query)
        answer = llm.generate(prompt)
        logging.info("ANSWER (no RAG)")
        print(answer)
        return

    embedder = Embedder()
    os.makedirs(config.CACHE_DIR, exist_ok=True)

    if args.store == "numpy":
        embeddings_path = os.path.join(config.CACHE_DIR, "embeddings.npy")
        chunks_path = os.path.join(config.CACHE_DIR, "chunks.json")
        if os.path.exists(embeddings_path) and os.path.exists(chunks_path):
            logging.info("Loading from numpy cache...")
            with open(chunks_path) as f:
                chunked_docs = json.load(f)
            doc_embeddings = np.load(embeddings_path)
        else:
            docs = load_pdfs(data_path)
            chunked_docs = chunk_documents(docs)
            doc_embeddings = embedder.embed_documents([d["text"] for d in chunked_docs])
            np.save(embeddings_path, doc_embeddings)
            with open(chunks_path, "w") as f:
                json.dump(chunked_docs, f)
            logging.info("Embeddings saved to numpy cache.")
        retriever = Retriever(chunked_docs, doc_embeddings)

    else:  # faiss
        import faiss
        store = ChunkStore(config.SQLITE_DB_PATH)
        if os.path.exists(config.FAISS_INDEX_PATH) and store.exists():
            logging.info("Loading from FAISS + SQLite cache...")
            chunked_docs = store.load()
            index = faiss.read_index(config.FAISS_INDEX_PATH)
            retriever = RetrieverFAISS.from_index(chunked_docs, index)
        else:
            docs = load_pdfs(data_path)
            chunked_docs = chunk_documents(docs)
            doc_embeddings = embedder.embed_documents([d["text"] for d in chunked_docs])
            store.save(chunked_docs)
            retriever = RetrieverFAISS(chunked_docs, doc_embeddings)
            faiss.write_index(retriever.index, config.FAISS_INDEX_PATH)
            logging.info("Embeddings saved to FAISS + SQLite cache.")

    query_embedding = embedder.embed_query(args.query)
    results = retriever.retrieve(query_embedding, top_k=top_k)

    contexts = [r["text"] for r in results]
    rag_prompt = build_prompt_rag(args.query, contexts)

    answer = llm.generate(rag_prompt)
    print("\nANSWER:\n")
    print(answer)


if __name__ == "__main__":
    main()
