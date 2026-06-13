"""Query page: ask one question and see the answer plus the retrieved chunks."""

from typing import Any

import streamlit as st

from api_client import APIError, get_presets, post_query_stream
from ui import render_chunks, render_hyde_doc

st.title("Query")
st.write("Ask one question. Use a preset, or switch to Advanced to set an inline config.")

try:
    presets = get_presets()
except APIError as exc:
    st.error(str(exc))
    st.stop()

mode = st.radio("Configuration", ["Preset", "Advanced"], horizontal=True)

config: str | dict[str, Any]
if mode == "Preset":
    names = sorted(presets)
    config = st.selectbox("Preset", names, index=names.index("best") if "best" in names else 0)
else:
    backend = st.selectbox("backend", ["ollama", "gpt"])
    if backend == "gpt":
        st.caption("gpt needs OPENAI_API_KEY set on the server.")

    # The retrieval knobs (and HyDE) are greyed when no_rag is on; they have no effect without retrieval.
    no_rag = st.checkbox("no_rag (skip retrieval)")
    retriever = st.selectbox("retriever", ["dense", "bm25", "hybrid"], disabled=no_rag)
    top_k = st.slider("top_k", min_value=1, max_value=50, value=15, disabled=no_rag)
    rerank = st.checkbox("rerank (cross-encoder)", disabled=no_rag)
    hyde = st.checkbox("hyde (embed a hypothetical answer)", disabled=no_rag)

    config = {"no_rag": no_rag, "backend": backend}
    if not no_rag:
        config.update({"retriever": retriever, "top_k": top_k, "rerank": rerank, "hyde": hyde})

query = st.text_area("Question", placeholder="What is the difference between RAG-Sequence and RAG-Token?")

if st.button("Run", type="primary"):
    if not query.strip():
        st.warning("Enter a question first.")
        st.stop()
    try:
        with st.spinner("Retrieving..."):
            meta, tokens = post_query_stream(query, config)

        st.subheader("Answer")
        st.write_stream(tokens)  # renders tokens live as they arrive
    except APIError as exc:
        st.error(str(exc))
        st.stop()

    render_hyde_doc(meta.get("hyde_doc"))

    st.subheader("Retrieved chunks")
    render_chunks(meta["chunks"])

    with st.expander("Resolved config"):
        st.json(meta["config"])
