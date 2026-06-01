def build_prompt_no_rag(query: str) -> str:
    return f"""
Answer the following question:

Question:

{query}

Answer:

"""


def build_prompt_rag(query: str, contexts: list[str]) -> str:

    context_text = "\n\n".join(contexts)

    return f"""

Answer the question using only the context below.
If the context contains specific numbers, scores, or statistics relevant to the question, quote them directly and attribute them to the correct model or entity.
If the answer is not in the context, say so.

Context:

{context_text}

Question:

{query}

Answer:

"""

