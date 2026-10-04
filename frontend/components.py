"""
Reusable Streamlit UI components for DC Roommate Slang Bridge.
"""
from typing import Any, Dict, List
import streamlit as st
from backend.models import DictionaryTerm, TranslationBreakdown


def render_header(status_data: Dict[str, Any]):
    """Renders the top hero banner with campus status badges."""
    is_ollama = status_data.get("ollama_connected", False)
    selected_model = status_data.get("selected_model", "llama3")
    terms_count = status_data.get("dictionary_terms_count", 0)

    ollama_badge = (
        f'<span class="dc-pill-badge active">⚡ Ollama Active ({selected_model})</span>'
        if is_ollama
        else '<span class="dc-pill-badge offline">🛡️ Local Offline Engine (Zero Cloud)</span>'
    )

    st.markdown(
        f"""
        <div class="dc-hero-banner">
            <div class="dc-hero-title">
                <span>🏛️ DC Roommate Slang Bridge</span>
            </div>
            <div class="dc-hero-subtitle">
                The local-first cultural translator & roommate linguistic bridge for <b>Infosys Mysore DC</b> trainees.
                Decode regional slang, GEC academic panic, JC food court plans, and ECC hostel banter with 100% offline privacy.
            </div>
            <div class="dc-badge-row">
                <span class="dc-pill-badge">📍 337-Acre Mysore DC</span>
                <span class="dc-pill-badge">🏢 GEC 1 & 2 • JC Multiplex • ECC</span>
                <span class="dc-pill-badge">📖 {terms_count} Grounded Slang Terms</span>
                {ollama_badge}
                <span class="dc-pill-badge">🔒 100% Offline • Hostel Wi-Fi Resilient</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_breakdown_card(breakdown: TranslationBreakdown):
    """
    Renders the exact required 3-part breakdown:
    1. Direct Meaning / Translation
    2. The Vibe / Tone
    3. On-Campus Context (JC, GEC, or hostel life)
    Along with cultural nuances and suggested roommate reply.
    """
    # Matched Terms Pills
    tags_html = ""
    for term in breakdown.matched_terms:
        tags_html += f'<span class="slang-tag">📌 {term}</span>'

    if not tags_html:
        tags_html = '<span class="slang-tag">🔍 Conversational Campus Lingo</span>'

    # Cultural Nuances HTML
    nuances_html = ""
    if breakdown.cultural_nuances:
        items = "".join([f"<li>{item}</li>" for item in breakdown.cultural_nuances])
        nuances_html = f"""
        <div style="margin-top: 14px; background: rgba(30, 41, 59, 0.6); padding: 12px 16px; border-radius: 8px; border: 1px solid #334155;">
            <div style="color: #94a3b8; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; margin-bottom: 6px;">
                🌐 Cultural & Linguistic Nuances
            </div>
            <ul style="color: #cbd5e1; font-size: 0.95rem; margin: 0; padding-left: 20px; line-height: 1.5;">
                {items}
            </ul>
        </div>
        """

    # Roommate Reply Suggestion HTML
    reply_html = ""
    if breakdown.roommate_reply_suggestion:
        reply_html = f"""
        <div class="card-reply">
            <div class="card-title-reply">
                <span>💬 Suggested Roommate Response</span>
            </div>
            <div class="card-body-reply">
                "{breakdown.roommate_reply_suggestion}"
            </div>
        </div>
        """

    card_html = f"""
    <div style="margin-top: 20px;">
        <div style="margin-bottom: 12px;">
            <span style="color: #94a3b8; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;">Detected Campus Terms:</span><br/>
            <div style="margin-top: 6px;">{tags_html}</div>
        </div>

        <!-- 1. Direct Meaning / Translation -->
        <div class="output-card card-meaning">
            <div class="card-title-meaning">
                <span>📘 Direct Meaning / Translation</span>
            </div>
            <div class="card-body-meaning">
                {breakdown.direct_meaning}
            </div>
        </div>

        <!-- 2. The Vibe / Tone -->
        <div class="output-card card-vibe">
            <div class="card-title-vibe">
                <span>🎭 The Vibe & Tone</span>
            </div>
            <div class="card-body-vibe">
                {breakdown.vibe_and_tone}
            </div>
        </div>

        <!-- 3. On-Campus Context -->
        <div class="output-card card-context">
            <div class="card-title-context">
                <span>🏛️ On-Campus Context (JC, GEC, or Hostel Life)</span>
            </div>
            <div class="card-body-context">
                {breakdown.on_campus_context}
            </div>
        </div>

        {reply_html}
        {nuances_html}

        <div class="model-info-footer">
            <span>⚙️ Engine: <b>{breakdown.model_used}</b></span>
            <span>🛡️ Grounding: <b>Local Campus Dictionary</b></span>
            <span>🔒 Zero Cloud Telemetry</span>
        </div>
    </div>
    """

    st.markdown(card_html, unsafe_allow_html=True)


def render_term_card(term: DictionaryTerm):
    """Renders a single campus dictionary term card."""
    lang_pills = " ".join([f'<span class="slang-tag" style="font-size: 0.72rem;">{l}</span>' for l in term.languages])
    alias_str = f" <i>(Aliases: {', '.join(term.aliases)})</i>" if term.aliases else ""

    st.markdown(
        f"""
        <div style="background: #111e33; border: 1px solid #1e3355; border-radius: 10px; padding: 14px 16px; margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
                <div>
                    <span style="font-size: 1.15rem; font-weight: 700; color: #38bdf8;">{term.term}</span>
                    <span style="color: #64748b; font-size: 0.85rem;">{alias_str}</span>
                </div>
                <div>{lang_pills}</div>
            </div>
            <div style="color: #f1f5f9; font-size: 0.95rem; margin-bottom: 8px;">
                <b>Meaning:</b> {term.meaning}
            </div>
            <div style="color: #c084fc; font-size: 0.88rem; margin-bottom: 6px;">
                <b>Vibe:</b> {term.vibe}
            </div>
            <div style="color: #34d399; font-size: 0.88rem; margin-bottom: 8px;">
                <b>Campus Context:</b> {term.campus_context}
            </div>
            <div style="background: rgba(0,0,0,0.25); border-left: 3px solid #f59e0b; padding: 6px 10px; border-radius: 4px; color: #fde68a; font-size: 0.85rem;">
                💬 <i>"{term.example_usage}"</i>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
