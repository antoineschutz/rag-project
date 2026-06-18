"""Streamlit dashboard entry point for the RAG pipeline.

Run with `streamlit run dashboard/Home.py` (with the API server up). Streamlit auto-discovers
the pages under dashboard/pages/ and lists them in the sidebar.
"""

import streamlit as st

from api_client import API_URL, demo_mode, health

st.set_page_config(page_title="RAG pipeline", page_icon="🔎", layout="wide")

st.title("🔎 RAG pipeline dashboard")
st.write(
    "A browser UI over the from-scratch RAG pipeline. Ask questions, compare two "
    "configurations side by side, and browse evaluation results."
)

if health():
    st.success(f"API connected at {API_URL}")
else:
    st.error(
        f"API not reachable at {API_URL}. Start it in another terminal:\n\n"
        "```\nuvicorn src.api.server:app --reload\n```\n\n"
        "Set `RAG_API_URL` if the server runs elsewhere."
    )

st.divider()
st.subheader("Pages")
st.markdown(
    "- **Query**: ask one question and see the answer plus the retrieved chunks.\n"
    "- **Compare**: run one question through two configs (e.g. RAG vs no-RAG) side by side.\n"
    "- **Evaluate**: chart benchmark results, or run a live evaluation over the QA set.\n"
    "- **Chat**: hold a multi-turn conversation; follow-up questions are rewritten into a standalone query before retrieval."
)

st.divider()
if demo_mode():
    st.caption(
        "Hosted demo on Google Cloud Run (Groq free-tier, scales to zero, so the first request "
        "after idle is a slow cold start). Source: https://github.com/antoineschutz/rag-project"
    )
else:
    st.caption("Run both processes:")
    st.code(
        "uvicorn src.api.server:app --reload   # terminal 1\n"
        "streamlit run dashboard/Home.py       # terminal 2",
        language="bash",
    )
