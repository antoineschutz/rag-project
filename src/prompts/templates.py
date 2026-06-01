def build_prompt_no_rag(query: str) -> str:
    return f"""Answer the following question as accurately as possible.
If you don't know the answer, say so.

Question:

{query}

Answer:

"""


def build_prompt_rag(query: str, contexts: list[str]) -> str:
    context_text = "\n\n".join(contexts)
    return f"""Answer the following question using only the context below.
If the answer is not in the context, say so.

Context:

{context_text}

Question:

{query}

Answer:

"""
