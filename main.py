import argparse
import logging

from src.config import config
from src.embeddings.embed import Embedder
from src.retrieval.retriever_cosine import build_cosine_retriever
from src.retrieval.retriever_faiss import build_faiss_retriever
from src.retrieval.retriever_bm25 import build_bm25_retriever
from src.retrieval.retriever_hybrid import build_hybrid_retriever
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
        "--hyde",
        action="store_true",
        help="Use HyDE: embed a hypothetical answer passage instead of the raw query",
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

    if args.retriever == "bm25":
        retriever = build_bm25_retriever(data_path)
        results = retriever.retrieve(args.query, top_k=top_k)
    else:
        embedder = Embedder()

        if args.hyde:
            from src.hyde.hyde import generate_hypothetical_doc
            embed_input = generate_hypothetical_doc(args.query, llm)
        else:
            embed_input = args.query

        query_embedding = embedder.embed_query(embed_input)

        if args.retriever == "hybrid":
            retriever = build_hybrid_retriever(
                data_path, embedder, args.store, args.index_type,
                fusion=args.fusion, alpha=args.alpha,
            )
            results = retriever.retrieve(args.query, query_embedding, top_k=top_k)
        else:
            if args.store == "faiss":
                retriever = build_faiss_retriever(data_path, embedder, index_type=args.index_type)
            else:
                retriever = build_cosine_retriever(data_path, embedder)
            results = retriever.retrieve(query_embedding, top_k=top_k)

    contexts = [r["text"] for r in results]
    rag_prompt = build_prompt_rag(args.query, contexts)

    answer = llm.generate(rag_prompt)
    print("\nANSWER:\n")
    print(answer)


if __name__ == "__main__":
    main()
