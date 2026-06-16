"""Query page: ask one question and see the answer plus the retrieved chunks."""

import streamlit as st

from api_client import APIError, get_presets, get_sources, post_query_stream
from ui import config_selector, render_chunks, render_hyde_doc

st.title("Query")
st.write("Ask one question. Use a preset, or switch to Advanced to set an inline config.")

try:
    presets = get_presets()
    sources = get_sources()
except APIError as exc:
    st.error(str(exc))
    st.stop()

with st.sidebar:
    st.header("Configuration")
    config = config_selector(presets, sources=sources, key="query")

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
