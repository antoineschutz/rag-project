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


def render_standalone_query(standalone: str | None, original: str) -> None:
    """Show the condensed standalone query when chat history rewrote the user's follow-up."""
    if not standalone or standalone == original:
        return
    with st.expander("Standalone query (rewritten from your follow-up for retrieval)"):
        st.write(standalone)


def config_selector(presets: dict[str, Any], key: str = "cfg") -> str | dict[str, Any]:
    """Render the Preset/Advanced config picker; return a preset name or an inline knob dict.

    `key` namespaces the widgets so different pages can render the picker independently.
    """
    mode = st.radio("Configuration", ["Preset", "Advanced"], horizontal=True, key=f"{key}_mode")
    if mode == "Preset":
        names = sorted(presets)
        return st.selectbox(
            "Preset", names,
            index=names.index("best") if "best" in names else 0, key=f"{key}_preset",
        )

    backend = st.selectbox("backend", ["ollama", "gpt"], key=f"{key}_backend")
    if backend == "gpt":
        st.caption("gpt needs OPENAI_API_KEY set on the server.")

    # The retrieval knobs (and HyDE) are greyed when no_rag is on; they have no effect without retrieval.
    no_rag = st.checkbox("no_rag (skip retrieval)", key=f"{key}_no_rag")
    retriever = st.selectbox("retriever", ["dense", "bm25", "hybrid"], disabled=no_rag, key=f"{key}_retriever")
    top_k = st.slider("top_k", min_value=1, max_value=50, value=15, disabled=no_rag, key=f"{key}_top_k")
    rerank = st.checkbox("rerank (cross-encoder)", disabled=no_rag, key=f"{key}_rerank")
    hyde = st.checkbox("hyde (embed a hypothetical answer)", disabled=no_rag, key=f"{key}_hyde")

    config: dict[str, Any] = {"no_rag": no_rag, "backend": backend}
    if not no_rag:
        config.update({"retriever": retriever, "top_k": top_k, "rerank": rerank, "hyde": hyde})
    return config
