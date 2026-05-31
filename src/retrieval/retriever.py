import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from src.config import config


class Retriever:
    def __init__(self, chunked_docs, doc_embeddings, verbose=False):
        self.docs = chunked_docs
        self.embeddings = doc_embeddings
        self.verbose = verbose

    def retrieve(self, query_embedding, top_k=config.TOP_K):
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]

        top_indices = np.argsort(similarities)[-top_k:][::-1]

        results = []
        for i in top_indices:
            results.append({
                "text": self.docs[i]["text"],
                "source": self.docs[i]["source"],
                "score": float(similarities[i])
            })

        if self.verbose:
            print("\nTop-k retrieval results:\n")

            for r in results:
                print(f"{r['score']:.4f} |  {r['text']} | {len(r['text'])}") # {r['source']} -> (removing the source for now since i'm using only one source for testing)

           
        return results