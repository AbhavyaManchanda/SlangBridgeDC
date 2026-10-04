"""
Reusable Streamlit UI components for DC Roommate Slang Bridge.
"""
from typing import Any, Dict, List
import streamlit as st
from backend.models import DictionaryTerm, TranslationBreakdown


def render_header(status_data: Dict[str, Any]):
    """Renders the top hero banner with campus status badges using native Streamlit elements."""
    is_ollama = status_data.get("ollama_connected", False)
    selected_model = status_data.get("selected_model", "llama3")
    terms_count = status_data.get("dictionary_terms_count", 0)

    st.title("🏛 DC Roommate Slang Bridge")
    st.markdown(
        "The local-first cultural translator & roommate linguistic bridge for **Infosys Mysore DC** trainees. "
        "Decode regional slang, GEC academic panic, JC food court plans, and ECC hostel banter with 100% offline privacy."
    )
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.info("📍 337-Acre Mysore DC")
    with col2:
        st.info("🏢 GEC, JC & ECC")
    with col3:
        st.info(f"📖 {terms_count} Slang Terms")
    with col4:
        if is_ollama:
            st.success(f"⚡ Ollama Active ({selected_model})")
        else:
            st.warning("🛡️ Local Offline Engine")
    with col5:
        st.success("🔒 100% Offline")
    st.markdown("---")


def render_breakdown_card(breakdown: TranslationBreakdown):
    """
    Renders the exact required 3-part breakdown using clean structured lists:
    1. Direct Meaning / Translation
    2. The Vibe / Tone
    3. On-Campus Context (JC, GEC, or hostel life)
    Along with cultural nuances and suggested roommate reply.
    """
    st.markdown("### 📌 Detected Campus Terms")
    terms_to_show = breakdown.matched_terms if breakdown.matched_terms else ["Conversational Campus Lingo"]
    st.markdown(" ".join([f"`📌 {term}`" for term in terms_to_show]))

    # 1. Direct Meaning / Translation
    with st.container():
        st.subheader("📘 Direct Meaning / Translation")
        raw_meaning = breakdown.direct_meaning
        if "|" in raw_meaning:
            parts = [p.strip() for p in raw_meaning.split("|") if p.strip()]
            for part in parts:
                st.markdown(f"- {part}")
        else:
            st.info(raw_meaning)

    # 2. The Vibe / Tone
    with st.container():
        st.subheader("🎭 The Vibe & Tone")
        st.warning(breakdown.vibe_and_tone)

    # 3. On-Campus Context
    with st.container():
        st.subheader("🏛️️ On-Campus Context (JC, GEC, or Hostel Life)")
        st.success(breakdown.on_campus_context)

    # Roommate Reply Suggestion
    if breakdown.roommate_reply_suggestion:
        st.markdown("### 💬 Suggested Roommate Response")
        st.code(breakdown.roommate_reply_suggestion, language="text")

    # Cultural Nuances
    if breakdown.cultural_nuances:
        st.markdown("### 🌐 Cultural & Linguistic Nuances")
        for nuance in breakdown.cultural_nuances:
            st.markdown(f"- {nuance}")

    st.markdown("---")
    st.caption(f"⚙️ Engine: **{breakdown.model_used}** | 🛡️ Grounding: **Local Campus Dictionary** | 🔒 Zero Cloud Telemetry")


def render_term_card(term: DictionaryTerm):
    """Renders a single campus dictionary term card using clean Markdown."""
    languages_str = ", ".join(term.languages) if term.languages else "Campus Lingo"
    aliases_str = f" (Aliases: {', '.join(term.aliases)})" if term.aliases else ""

    with st.container():
        st.markdown(f"### 🔤 {term.term}{aliases_str}")
        st.caption(f"**Languages:** {languages_str} | **Category:** {term.category}")
        st.markdown(f"**Meaning:** {term.meaning}")
        st.markdown(f"**Vibe:** {term.vibe}")
        st.markdown(f"**Campus Context:** {term.campus_context}")
        if term.example_usage:
            st.info(f"💬 Example: \"{term.example_usage}\"")
        st.markdown("---")