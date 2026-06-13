"""Small shared rendering helpers for the dashboard pages."""

from typing import Any

import streamlit as st


def render_hyde_doc(doc: str | None) -> None:
    """Show the HyDE hypothetical passage (the text embedded for retrieval) when present."""
    if not doc:
        return
    with st.expander("HyDE hypothetical passage (embedded instead of your question)"):
        st.write(doc)


def render_chunks(chunks: list[dict[str, Any]]) -> None:
    """Render retrieved chunks as expanders (source + score in the header, text inside)."""
    if not chunks:
        st.caption("No chunks retrieved (no-RAG path).")
        return
    st.caption(f"{len(chunks)} retrieved chunks")
    for i, c in enumerate(chunks, start=1):
        header = f"{i}. {c.get('source', '?')}  ·  score {c.get('score', 0.0):.3f}"
        with st.expander(header):
            st.write(c.get("text", ""))
