"""Compare page: run one question through two configs side by side (e.g. RAG vs no-RAG)."""

import streamlit as st

from api_client import APIError, get_presets, post_compare
from ui import render_chunks

st.title("Compare")
st.write("Run one question through two presets and see both answers and chunks side by side.")

try:
    presets = get_presets()
except APIError as exc:
    st.error(str(exc))
    st.stop()

names = sorted(presets)
col_a, col_b = st.columns(2)
with col_a:
    a = st.selectbox("Config A", names, index=names.index("baseline") if "baseline" in names else 0)
with col_b:
    b = st.selectbox("Config B", names, index=names.index("no-rag") if "no-rag" in names else 0)

query = st.text_area("Question", placeholder="What is salient span masking?")

if st.button("Compare", type="primary"):
    if not query.strip():
        st.warning("Enter a question first.")
        st.stop()
    try:
        with st.spinner("Running both configs..."):
            result = post_compare(query, a, b)
    except APIError as exc:
        st.error(str(exc))
        st.stop()

    left, right = st.columns(2)
    for col, label, side in ((left, a, result["a"]), (right, b, result["b"])):
        with col:
            st.subheader(label)
            st.write(side["answer"])
            render_chunks(side["chunks"])
            with st.expander("Config"):
                st.json(side["config"])
