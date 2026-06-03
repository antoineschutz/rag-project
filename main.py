import argparse
import logging

from src.config import config
from src.embeddings.embed import Embedder
from src.retrieval.factory import build_retriever
from src.prompts.templates import build_prompt_rag, build_prompt_no_rag
from src.llm.client import LLMClient

logger = logging.getLogger(__name__)


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
    parser.add_argument(
        "--index-type",
        choices=["flat", "ivf"],
        default="flat",
        dest="index_type",
        help="FAISS index type, only applies with --store faiss (default: flat)",
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
        print("ANSWER (no RAG)")
        print(answer)
        return

    embedder = Embedder()
    retriever = build_retriever(args.store, data_path, embedder, index_type=args.index_type)

    query_embedding = embedder.embed_query(args.query)
    results = retriever.retrieve(query_embedding, top_k=top_k)

    contexts = [r["text"] for r in results]
    rag_prompt = build_prompt_rag(args.query, contexts)

    answer = llm.generate(rag_prompt)
    print("\nANSWER:\n")
    print(answer)


if __name__ == "__main__":
    main()
