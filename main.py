import argparse
import logging

from src.config import split_config
from src.pipeline import answer_query
from src.retrieval.factory import build_index


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the RAG pipeline.")
    parser.add_argument("--query", required=True, help="Question to ask the model")
    parser.add_argument("--data-path", default=None, help="Path to PDF data directory")
    parser.add_argument("--backend", choices=["ollama", "gpt"], default=None, help="LLM backend")
    parser.add_argument("--model", default=None, help="Model name override")
    parser.add_argument("--embed-model", default=None, dest="embed_model",
                        help="Sentence-transformers embedding model (overrides config)")
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
    parser.add_argument(
        "--retriever",
        choices=["dense", "bm25", "hybrid"],
        default="dense",
        help="Retrieval method: dense, bm25, or hybrid (default: dense)",
    )
    parser.add_argument(
        "--fusion",
        choices=["rrf", "weighted"],
        default="rrf",
        help="Fusion strategy for --retriever hybrid (default: rrf)",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.5,
        help="Dense weight for weighted sum fusion, between 0 and 1 (default: 0.5)",
    )
    parser.add_argument(
        "--rerank",
        action="store_true",
        help="Re-rank retrieved chunks with a cross-encoder before generation",
    )
    parser.add_argument(
        "--hyde",
        action="store_true",
        help="Use HyDE: embed a hypothetical answer passage instead of the raw query",
    )
    parser.add_argument(
        "--num-ctx",
        type=int,
        default=None,
        dest="num_ctx",
        help="Ollama context window in tokens (default: env.OLLAMA_NUM_CTX = 4096)",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s — %(message)s")
    for name in ("__main__", "src"):
        logging.getLogger(name).setLevel(args.log_level)

    # Map the parsed args onto the three param groups (unknown keys like log_level are ignored).
    index_params, retrieval_params, generation_params = split_config(vars(args), args.query)

    retriever = None if generation_params.no_rag else build_index(index_params)
    result = answer_query(retriever, retrieval_params, generation_params)

    print("\nANSWER:\n")
    print(result["answer"])


if __name__ == "__main__":
    main()
