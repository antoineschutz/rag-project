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


def run_pipeline(
    query: str,
    data_path: str | None = None,
    backend: str | None = None,
    model: str | None = None,
    embed_model: str | None = None,
    top_k: int | None = None,
    no_rag: bool = False,
    store: str = "numpy",
    index_type: str = "flat",
    retriever: str = "dense",
    fusion: str = "rrf",
    alpha: float = 0.5,
    rerank: bool = False,
    hyde: bool = False,
) -> str:
    resolved_backend = backend or config.LLM_BACKEND
    resolved_top_k = top_k or config.TOP_K
    resolved_data_path = data_path or config.DATA_PATH

    llm = LLMClient(backend=resolved_backend, model=model)

    if no_rag:
        return llm.generate(build_prompt_no_rag(query))

    retrieval_k = resolved_top_k * 3 if rerank else resolved_top_k

    if retriever == "bm25":
        ret = build_bm25_retriever(resolved_data_path)
        results = ret.retrieve(query, top_k=retrieval_k)
    else:
        embedder = Embedder(model_name=embed_model or config.EMBED_MODEL)

        if hyde:
            from src.hyde.hyde import generate_hypothetical_doc
            embed_input = generate_hypothetical_doc(query, llm)
        else:
            embed_input = query

        query_embedding = embedder.embed_query(embed_input)

        if retriever == "hybrid":
            ret = build_hybrid_retriever(
                resolved_data_path, embedder, store, index_type,
                fusion=fusion, alpha=alpha,
            )
            results = ret.retrieve(query, query_embedding, top_k=retrieval_k)
        else:
            if store == "faiss":
                ret = build_faiss_retriever(resolved_data_path, embedder, index_type=index_type)
            else:
                ret = build_cosine_retriever(resolved_data_path, embedder)
            results = ret.retrieve(query_embedding, top_k=retrieval_k)

    if rerank:
        from src.reranker.reranker import Reranker
        results = Reranker().rerank(query, results, top_k=resolved_top_k)

    contexts = [r["text"] for r in results]
    return llm.generate(build_prompt_rag(query, contexts))


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
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s — %(message)s")
    for name in ("__main__", "src"):
        logging.getLogger(name).setLevel(args.log_level)

    answer = run_pipeline(
        query=args.query,
        data_path=args.data_path,
        backend=args.backend,
        model=args.model,
        embed_model=args.embed_model,
        top_k=args.top_k,
        no_rag=args.no_rag,
        store=args.store,
        index_type=args.index_type,
        retriever=args.retriever,
        fusion=args.fusion,
        alpha=args.alpha,
        rerank=args.rerank,
        hyde=args.hyde,
    )
    print("\nANSWER:\n")
    print(answer)


if __name__ == "__main__":
    main()
