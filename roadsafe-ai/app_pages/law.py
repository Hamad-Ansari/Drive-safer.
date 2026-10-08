"""Traffic Law Assistant — cited, extractive-by-default chat with refusals."""
from __future__ import annotations

import streamlit as st

from roadsafe.core import config
from roadsafe.services import law_assistant as la


@st.cache_resource(show_spinner="Indexing law corpus…")
def get_retriever() -> la.LawRetriever:
    sections = la.load_corpus()
    return la.LawRetriever(sections), sections


def _badge(jurisdiction: str) -> str:
    cls = {"National": "rs-badge-national", "Punjab": "rs-badge-punjab"}.get(jurisdiction, "rs-badge-both")
    return f"<span class='rs-badge {cls}'>{jurisdiction}</span>"


def _render_sources(sources: list[la.LawSection]) -> None:
    with st.expander("📚 Sources (open passage)"):
        for s in sources:
            st.markdown(
                f"{_badge(s.jurisdiction)}  \n**{s.doc}** — `{s.id}`  \n"
                f"**{s.heading}.** {s.text}  \n"
                f"<small>Version: {s.version} · <a href='{s.source_url}' target='_blank' "
                f"rel='noopener noreferrer'>official source ↗</a></small>",
                unsafe_allow_html=True)


def render() -> None:
    st.title("⚖️ Traffic Law Assistant")
    st.caption("Answers only from the demo corpus (National + Punjab), always cited. "
               "It refuses rather than invent. " + config.LAW_NOTE)

    retriever, sections = get_retriever()
    llm_cfg = config.get_llm_config()

    st.markdown(
        f"Scope: **{st.session_state.get('law_scope', 'Both')}** · Mode: "
        f"**{'LLM + citation enforcer' if llm_cfg else 'Extractive (no LLM — cannot hallucinate)'}**",
        help="Set ROADSAFE_LLM_* env vars to enable a generative mode; citations are still enforced.")

    if "law_messages" not in st.session_state:
        st.session_state["law_messages"] = []

    chips = st.columns(len(la.SUGGESTED_QUESTIONS[:4]))
    for col, q in zip(chips, la.SUGGESTED_QUESTIONS[:4]):
        if col.button(q, key=f"sug_{q}", use_container_width=True):
            st.session_state["law_pending"] = q
            st.rerun()

    for msg in st.session_state["law_messages"]:
        with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "⚖️"):
            st.markdown(msg["content"])
            if msg.get("sources"):
                _render_sources(msg["sources"])
            if msg.get("refused"):
                st.caption("Refusal: the corpus did not cover this — no answer was invented.")

    pending = st.session_state.pop("law_pending", None)
    user_q = pending or st.chat_input("Ask about a traffic rule… (English)")
    if user_q:
        st.session_state["law_messages"].append({"role": "user", "content": user_q})
        with st.chat_message("user", avatar="🧑"):
            st.markdown(user_q)
        with st.chat_message("assistant", avatar="⚖️"):
            with st.spinner("Searching the corpus…"):
                result = la.answer_question(user_q, retriever,
                                            scope=st.session_state.get("law_scope", "Both"),
                                            llm_cfg=llm_cfg)
            st.markdown(result["answer"])
            if result["sources"]:
                _render_sources(result["sources"])
            if result["refused"]:
                st.caption("Refusal: the corpus did not cover this — no answer was invented.")
            st.caption(la.corpus_notice(sections))
        st.session_state["law_messages"].append({
            "role": "assistant", "content": result["answer"],
            "sources": result["sources"], "refused": result["refused"]})
        st.rerun()
