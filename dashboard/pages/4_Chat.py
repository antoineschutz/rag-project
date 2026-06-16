"""Chat page: a multi-turn conversation where follow-ups are resolved against the history.

The page holds the conversation in st.session_state and sends the prior turns with each request.
The server condenses a context-dependent follow-up into a standalone query before retrieval, so
"how does it differ?" retrieves correctly. The server itself stays stateless.

Each assistant turn keeps its retrieved chunks (and standalone query / HyDE passage) so they can be
revealed again on later reruns, not just in the run that produced them.
"""

import streamlit as st

from api_client import APIError, get_presets, get_sources, post_query_stream
from ui import config_selector, render_chunks, render_hyde_doc, render_standalone_query

st.title("Chat")
st.write("Multi-turn chat. Follow-up questions are rewritten into a standalone query before retrieval.")

try:
    presets = get_presets()
    sources = get_sources()
except APIError as exc:
    st.error(str(exc))
    st.stop()

with st.sidebar:
    st.header("Configuration")
    config = config_selector(presets, sources=sources, key="chat")
    st.caption("Config applies per turn; you can change it mid-conversation.")
    if st.button("Clear conversation"):
        for stale in [k for k in st.session_state if k.startswith("sources_")]:
            del st.session_state[stale]
        st.session_state.chat_history = []
        st.rerun()

st.session_state.setdefault("chat_history", [])


def render_sources(msg: dict, key: str) -> None:
    """Render an assistant turn's extras: standalone query, HyDE passage, and a reveal for chunks.

    Chunks are gated behind a toggle (the outer layer); each chunk stays individually expandable
    inside, since Streamlit forbids nesting one expander inside another.
    """
    render_standalone_query(msg.get("standalone_query"), "")
    render_hyde_doc(msg.get("hyde_doc"))
    chunks = msg.get("chunks") or []
    if chunks and st.toggle(f"Reveal retrieved chunks ({len(chunks)})", key=key):
        render_chunks(chunks)


# Replay the conversation so far (content plus each assistant turn's revealable sources).
for i, msg in enumerate(st.session_state.chat_history):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"] == "assistant":
            render_sources(msg, key=f"sources_{i}")

if prompt := st.chat_input("Ask a question..."):
    with st.chat_message("user"):
        st.write(prompt)

    # History sent to the server is every turn BEFORE this new question (None on the first turn).
    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history]
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        try:
            with st.spinner("Reformulating and retrieving..." if history else "Retrieving..."):
                meta, tokens = post_query_stream(prompt, config, history=history or None)
            answer = st.write_stream(tokens)  # streams live; returns the full concatenated text
        except APIError as exc:
            st.error(str(exc))
            st.session_state.chat_history.pop()  # roll back the user turn so it is not resent
            st.stop()

        assistant_msg = {
            "role": "assistant",
            "content": answer,
            "chunks": meta["chunks"],
            "standalone_query": meta.get("standalone_query"),
            "hyde_doc": meta.get("hyde_doc"),
        }
        # Key matches the index this turn will have in the replay loop next rerun, so the toggle
        # state persists when the chunks are revealed.
        render_sources(assistant_msg, key=f"sources_{len(st.session_state.chat_history)}")

    st.session_state.chat_history.append(assistant_msg)
