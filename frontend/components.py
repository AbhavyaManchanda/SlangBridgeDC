"""
Reusable Streamlit UI components for DC Roommate Slang Bridge.
Uses clean Markdown formatting with st.markdown() instead of HTML div tags
to ensure proper native Streamlit rendering without indented code blocks.
"""
from typing import Any, Dict
import streamlit as st
from backend.models import DictionaryTerm, TranslationBreakdown


def render_header(status_data: Dict[str, Any]):
    """Renders the top hero banner with campus status badges using clean Markdown."""
    is_ollama = status_data.get("ollama_connected", False)
    selected_model = status_data.get("selected_model", "llama3")
    terms_count = status_data.get("dictionary_terms_count", 0)

    engine_badge = f"⚡ **Ollama Active** (`{selected_model}`)" if is_ollama else "🛡️ **Local Offline Engine** (Zero Cloud)"

    st.markdown(
        f"# 🏛️ DC Roommate Slang Bridge\n\n"
        f"**The local-first cultural translator & roommate linguistic bridge for Infosys Mysore DC trainees.**  \n"
        f"*Decode regional slang, GEC academic panic, JC food court plans, and ECC hostel banter with 100% offline privacy.*\n\n"
        f"`📍 337-Acre Mysore DC` • `🏢 GEC 1 & 2 • JC Multiplex • ECC` • `📖 {terms_count} Grounded Slang Terms` • {engine_badge} • `🔒 100% Offline`\n\n"
        f"---"
    )


def render_breakdown_card(breakdown: TranslationBreakdown):
    """
    Renders the exact required 3-part breakdown using clean Markdown:
    1. Direct Meaning / Translation
    2. The Vibe / Tone
    3. On-Campus Context (JC, GEC, or hostel life)
    Along with cultural nuances and suggested roommate reply.
    Zero HTML div tags, avoiding Streamlit indented code blocks.
    """
    md_content = breakdown.to_markdown() if hasattr(breakdown, "to_markdown") else (breakdown.formatted_markdown or "")

    if not md_content:
        # Fallback clean Markdown builder
        terms_badges = " ".join([f"`{t}`" for t in breakdown.matched_terms]) if breakdown.matched_terms else "`Conversational Campus Lingo`"
        nuances_bullets = "\n".join([f"- {item}" for item in breakdown.cultural_nuances]) if breakdown.cultural_nuances else "- Authentic campus cross-cultural dialogue"
        reply_block = f"#### 💬 Suggested Roommate Response\n> *\"{breakdown.roommate_reply_suggestion}\"*\n\n" if breakdown.roommate_reply_suggestion else ""

        md_content = (
            f"### 📘 Direct Meaning / Translation\n"
            f"> {breakdown.direct_meaning}\n\n"
            f"### 🎭 The Vibe & Tone\n"
            f"**{breakdown.vibe_and_tone}**\n\n"
            f"### 🏛️ On-Campus Context (JC, GEC, or Hostel Life)\n"
            f"{breakdown.on_campus_context}\n\n"
            f"---\n\n"
            f"{reply_block}"
            f"#### 🌐 Cultural & Linguistic Nuances\n"
            f"{nuances_bullets}\n\n"
            f"#### 🏷️ Detected Campus Terms\n"
            f"{terms_badges}\n\n"
            f"---\n"
            f"*⚙️ **Engine:** {breakdown.model_used}  |  🛡️ **Grounding:** Local Campus Dictionary  |  🔒 **100% Offline & Private***\n"
        )

    # Render natively in Streamlit with st.markdown
    st.markdown(md_content)


def render_term_card(term: DictionaryTerm):
    """Renders a single campus dictionary term card using clean Markdown."""
    aliases_str = f" *(Aliases: {', '.join(term.aliases)})*" if term.aliases else ""
    langs_str = " ".join([f"`{l}`" for l in term.languages])

    st.markdown(
        f"#### 📌 {term.term} {aliases_str}\n"
        f"{langs_str}\n\n"
        f"- **Meaning:** {term.meaning}\n"
        f"- **Vibe:** *{term.vibe}*\n"
        f"- **Campus Context:** {term.campus_context}\n\n"
        f"> 💬 *\"{term.example_usage}\"*\n\n"
        f"---"
    )
