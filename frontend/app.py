"""
Streamlit Dashboard for DC Roommate Slang Bridge.
Designed for Infosys Mysore DC fresh trainees.
Runs 100% offline with zero cloud API dependencies.
"""
import io
import os
from pathlib import Path
import streamlit as st
import requests
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.config import (
    BACKEND_URL,
    CAMPUS_NAME,
    DEFAULT_OLLAMA_MODEL,
    FALLBACK_OLLAMA_MODELS,
    OLLAMA_HOST,
)
from backend.audio_service import audio_service
from backend.dictionary_service import dictionary_service
from backend.models import AddTermRequest, TranslationBreakdown
from backend.ollama_service import ollama_service
from frontend.components import render_breakdown_card, render_header, render_term_card
from frontend.styles import CUSTOM_CSS

# Page Configuration
st.set_page_config(
    page_title="DC Roommate Slang Bridge | Infosys Mysore",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject Custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def get_system_status():
    """Fetches system status from backend or local service."""
    try:
        resp = requests.get(f"{BACKEND_URL}/health", timeout=1.5)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass

    # Direct fallback if backend API process is not running
    is_connected, available = ollama_service.check_connection()
    selected_model, _ = ollama_service.get_preferred_model()
    return {
        "status": "healthy",
        "ollama_connected": is_connected,
        "ollama_host": OLLAMA_HOST,
        "available_models": available,
        "selected_model": selected_model,
        "dictionary_terms_count": len(dictionary_service.get_all_terms()),
        "mode": "Ollama Local AI" if is_connected else "Offline Local Heuristic & Grounding Engine",
    }


def call_translate(text: str, model_name: str, context_hint: str = None) -> TranslationBreakdown:
    """Translates text via backend API or direct service."""
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/translate",
            json={"text": text, "model_name": model_name, "context_hint": context_hint},
            timeout=30.0,
        )
        if resp.status_code == 200:
            return TranslationBreakdown(**resp.json())
    except Exception:
        pass

    # Direct service call
    return ollama_service.translate(text=text, model_name=model_name, context_hint=context_hint)


def call_transcribe_audio(file_bytes: bytes, filename: str, context_hint: str = None, model_name: str = None):
    """Transcribes audio via backend API or direct service."""
    try:
        files = {"file": (filename, file_bytes, "audio/wav")}
        params = {}
        if context_hint:
            params["context_hint"] = context_hint
        if model_name:
            params["model_name"] = model_name

        resp = requests.post(
            f"{BACKEND_URL}/api/transcribe",
            files=files,
            params=params,
            timeout=40.0,
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass

    # Direct audio service fallback
    response_obj = audio_service.process_audio(
        file_bytes=file_bytes,
        filename=filename,
        context_hint=context_hint,
        model_name=model_name,
    )
    return response_obj.model_dump()


# --- Session State Initialization ---
if "input_text" not in st.session_state:
    st.session_state.input_text = "Macha GEC punch maarke direct JC mein milte hain, scene sorted hai."
if "context_hint" not in st.session_state:
    st.session_state.context_hint = "Hostel roommate message after lab"

status_data = get_system_status()

# --- Sidebar Configuration ---
with st.sidebar:
    st.markdown("### ⚙️ Engine & Campus Status")

    is_ollama = status_data.get("ollama_connected", False)
    if is_ollama:
        st.success(f"🟢 **Ollama Connected** (`{status_data.get('ollama_host')}`)")
        available_models = status_data.get("available_models", [])
        if not available_models:
            available_models = [DEFAULT_OLLAMA_MODEL]
        selected_model = st.selectbox(
            "Active Ollama Model",
            options=available_models,
            index=0,
            help="Models pulled in your local Ollama daemon.",
        )
    else:
        st.info("🛡️ **Offline Grounding Engine Active**\n\nOllama daemon standby at `127.0.0.1:11434`. Using local dictionary heuristic engine.")
        selected_model = st.selectbox(
            "Target Local Model",
            options=["llama3", "gemma2", "llama3.2", "mistral", "phi3"],
            index=0,
            help="Specify model to use when Ollama is started.",
        )

    st.markdown("---")
    st.markdown("### ⚡ Quick Slang Chips")
    st.caption("Click to load common Infosys Mysore roommate phrases:")

    sample_chips = [
        ("Macha JC chalo, FA mein scene contra ho gaya!", "Post-exam panic at GEC"),
        ("Roommate swalpa adjust maadi yaar, AC 24 pe rakho.", "Hostel room AC debate"),
        ("Bhai green cycle kisne gayab kar di? 9:15 punch hai!", "Morning biometric rush"),
        ("Educator semma gaandu aayitaaru, 4th test case fail.", "GEC lab coding tension"),
        ("Mama Oasis lo parotta thindama, dhimak kharab aypoyindi.", "Evening food court run"),
        ("FA1 mein 92 marks phod diya! Weekend multiplex sorted.", "High-score celebration"),
    ]

    for chip_text, hint in sample_chips:
        if st.button(f"👉 {chip_text[:32]}...", key=f"chip_{chip_text[:10]}", use_container_width=True):
            st.session_state.input_text = chip_text
            st.session_state.context_hint = hint
            st.rerun()

    st.markdown("---")
    st.markdown("### 📍 Infosys Mysore Quick Facts")
    st.markdown(
        """
        - **Area**: 337 acres in Hebbal, Mysuru
        - **Academics**: GEC 1 (Greek Pillars) & GEC 2
        - **Hostels**: ECC Blocks (1 to 90+)
        - **Hangout**: JC Multiplex & Oasis Food Court
        - **Rule #1**: Punch biometric before 9:15 AM!
        - **Rule #2**: Pass mark in FA is strictly 65%!
        """
    )
    st.caption("Zero cloud telemetry • Local-first privacy")


# --- Main Dashboard ---
render_header(status_data)

tabs = st.tabs([
    "💬 Slang & Banter Translator",
    "🎙️ Voice Note Audio Bridge",
    "📖 Mysore DC Campus Lexicon",
    "🛡️ Local-First & Wi-Fi Manifesto",
])

# ==============================================================================
# TAB 1: TEXT TRANSLATOR
# ==============================================================================
with tabs[0]:
    st.markdown("#### 💬 Decode Regional Slang & Hostel Banter")
    st.markdown(
        "Paste regional slang, cross-state roommate messages, or GEC lab chatter. "
        "The bridge will break it down into **Direct Meaning**, **The Vibe/Tone**, and **On-Campus Context**."
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        user_input = st.text_area(
            "Hostel / Mess / Campus Slang Input",
            value=st.session_state.input_text,
            height=110,
            placeholder="e.g., Macha JC chalo, FA mein scene contra ho gaya aliya...",
            help="Type slang containing campus locations (JC, GEC, ECC) or regional terms (Kannada, Malayalam, Hindi, Tamil, Telugu).",
        )
    with col2:
        context_input = st.text_input(
            "Context Hint (Optional)",
            value=st.session_state.context_hint,
            placeholder="e.g. Sent during FA exam",
            help="Helps the model tune into whether this is an exam, hostel, or food court situation.",
        )
        translate_btn = st.button("🚀 Translate Slang", type="primary", use_container_width=True)

    if translate_btn or (user_input and user_input != st.session_state.get("last_auto_run", "")):
        if user_input.strip():
            with st.spinner("Decoding campus slang with Infosys Mysore cultural grounding..."):
                breakdown = call_translate(
                    text=user_input.strip(),
                    model_name=selected_model,
                    context_hint=context_input.strip() if context_input else None,
                )
                render_breakdown_card(breakdown)
                st.session_state.last_auto_run = user_input
        else:
            st.warning("Please enter a slang phrase or click one of the quick chips in the sidebar.")


# ==============================================================================
# TAB 2: VOICE NOTE AUDIO BRIDGE
# ==============================================================================
with tabs[1]:
    st.markdown("#### 🎙️ Voice Note Audio Bridge")
    st.markdown(
        "Trainees frequently send audio voice notes on WhatsApp or Signal while rushing between ECC hostels and GEC. "
        "Upload a voice note audio file (`.wav`, `.mp3`, `.ogg`, `.m4a`) or select one of our pre-packaged campus samples."
    )

    audio_col1, audio_col2 = st.columns([1, 1])

    with audio_col1:
        st.markdown("##### 📁 Option A: Upload Voice Note File")
        uploaded_audio = st.file_uploader(
            "Upload voice recording",
            type=["wav", "mp3", "ogg", "m4a", "webm"],
            help="Voice notes from roommates or batchmates.",
        )

    with audio_col2:
        st.markdown("##### 🎵 Option B: Pre-Packaged Campus Audio Samples")
        samples = audio_service.get_sample_voice_notes()
        sample_options = {s["filename"]: s for s in samples}

        selected_sample_name = st.selectbox(
            "Choose a test voice note",
            options=list(sample_options.keys()),
            help="Instant offline audio files synthesized with campus voice scenarios.",
        )

        chosen_sample = sample_options.get(selected_sample_name)
        if chosen_sample:
            st.caption(f"📝 Expected Transcript: *\"{chosen_sample['transcript']}\"*")
            with open(chosen_sample["path"], "rb") as f:
                sample_bytes = f.read()
            st.audio(sample_bytes, format="audio/wav")

    # Determine which audio to process
    active_audio_bytes = None
    active_filename = ""

    if uploaded_audio is not None:
        active_audio_bytes = uploaded_audio.getvalue()
        active_filename = uploaded_audio.name
        st.markdown("###### Preview Uploaded Audio:")
        st.audio(active_audio_bytes)
    elif chosen_sample:
        active_audio_bytes = sample_bytes
        active_filename = chosen_sample["filename"]

    st.markdown("---")
    transcribe_btn = st.button("🎧 Transcribe & Decode Voice Note", type="primary", use_container_width=True)

    if transcribe_btn and active_audio_bytes:
        with st.spinner("Processing audio locally and extracting cultural breakdown..."):
            audio_result = call_transcribe_audio(
                file_bytes=active_audio_bytes,
                filename=active_filename,
                context_hint="Hostel voice note recording",
                model_name=selected_model,
            )

            st.success("✅ Voice Note Processed Successfully!")
            st.markdown(
                f"""
                <div style="background: #0f172a; border: 1px solid #334155; padding: 14px 18px; border-radius: 10px; margin-bottom: 16px;">
                    <div style="color: #94a3b8; font-size: 0.85rem; font-weight: 700; text-transform: uppercase;">🎙️ Transcribed Audio Text:</div>
                    <div style="color: #f8fafc; font-size: 1.25rem; font-weight: 600; margin: 6px 0;">"{audio_result.get('transcribed_text')}"</div>
                    <div style="color: #64748b; font-size: 0.8rem;">
                        Duration: <b>{audio_result.get('duration_seconds')}s</b> | Engine: <b>{audio_result.get('engine_used')}</b> | File: <b>{audio_result.get('file_name')}</b>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            raw_breakdown = audio_result.get("breakdown")
            if raw_breakdown:
                breakdown = TranslationBreakdown(**raw_breakdown)
                render_breakdown_card(breakdown)


# ==============================================================================
# TAB 3: CAMPUS LEXICON
# ==============================================================================
with tabs[2]:
    st.markdown("#### 📖 Infosys Mysore Campus Dictionary")
    st.markdown("Explore structured terms, food court jargon, and multilingual roommate banter grounded in Mysore DC culture.")

    categories = dictionary_service.get_categories()
    category_options = {"all": "All Categories"}
    for c in categories:
        category_options[c["id"]] = c["name"]

    search_col1, search_col2 = st.columns([1, 2])
    with search_col1:
        cat_filter = st.selectbox(
            "Filter Category",
            options=list(category_options.keys()),
            format_func=lambda x: category_options[x],
        )
    with search_col2:
        search_query = st.text_input("🔍 Search Slang, Keyword, or Meaning", placeholder="e.g. JC, dosa, FA, contra, macha...")

    filtered_terms = dictionary_service.search_terms(query=search_query, category_id=cat_filter)
    st.caption(f"Showing **{len(filtered_terms)}** terms")

    term_col1, term_col2 = st.columns(2)
    for i, term in enumerate(filtered_terms):
        target_col = term_col1 if i % 2 == 0 else term_col2
        with target_col:
            render_term_card(term)

    # Section to add new campus slang
    st.markdown("---")
    with st.expander("➕ Contribute New Campus Slang / Mess Term (Saved Locally)"):
        with st.form("add_term_form"):
            st.markdown("##### Add an unlisted phrase to the local campus dictionary")
            add_term_name = st.text_input("Slang Term", placeholder="e.g., Maggi Point Chai")
            add_category = st.selectbox(
                "Category",
                options=[c["id"] for c in categories],
                format_func=lambda x: category_options.get(x, x),
            )
            add_languages = st.multiselect(
                "Languages / Origin",
                options=["Campus Lingo", "English", "Kannada", "Hindi", "Malayalam", "Tamil", "Telugu"],
                default=["Campus Lingo"],
            )
            add_meaning = st.text_input("Direct Meaning", placeholder="Quick tea and snack spot near ECC 60")
            add_vibe = st.text_input("Vibe / Tone", placeholder="Comforting, midnight cramming break")
            add_context = st.text_area("On-Campus Context", placeholder="Where trainees gather at 2 AM before FA assessments...")
            add_example = st.text_input("Example Usage", placeholder="Bhai chal Maggi point chalte hain...")
            submitted = st.form_submit_button("💾 Save to Local Dictionary")

            if submitted:
                if add_term_name and add_meaning and add_vibe and add_context:
                    try:
                        req = AddTermRequest(
                            term=add_term_name,
                            category=add_category,
                            languages=add_languages,
                            meaning=add_meaning,
                            vibe=add_vibe,
                            campus_context=add_context,
                            example_usage=add_example,
                        )
                        dictionary_service.add_term(req)
                        st.success(f"Term '{add_term_name}' added to local dictionary!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding term: {e}")
                else:
                    st.warning("Please fill out all required fields.")


# ==============================================================================
# TAB 4: PRIVACY & WI-FI MANIFESTO
# ==============================================================================
with tabs[3]:
    st.markdown("#### 🛡️ Local-First Architecture & Hostel Wi-Fi Resilience")
    st.markdown(
        """
        ### Why an Open-Source Local Approach Matters at Infosys Mysore DC

        Training at the **337-acre Infosys Mysore Development Centre** is a landmark phase for thousands of fresh engineering graduates. 
        However, the physical and digital realities of campus living make cloud-dependent AI tools impractical and risky.

        ---

        #### 1. 📶 Hostel Wi-Fi Bandwidth Throttling & Network Constraints
        - **Hostel Congestion**: In Employee Care Centre (ECC) hostel clusters housing 5,000+ trainees simultaneously streaming study videos, bandwidth drops severely in evenings and weekends.
        - **Strict Corporate Firewalls**: Infosys guest and training Wi-Fi networks block external AI API endpoints, unauthorized websocket connections, or enforce strict HTTP proxy policies.
        - **Zero Cloud Dependence**: **DC Roommate Slang Bridge** runs 100% on `localhost:8501` and `localhost:8000`. It requires **zero active internet connection**, zero external cloud credits, and zero cloud API keys. Even if the hostel router disconnects completely, the application continues to run without interruption.

        #### 2. 🔒 Absolute Privacy for Hostel Roommates
        - **Confidential Personal Banter**: Trainees live in twin-sharing rooms with strangers who quickly become lifelong friends. Private voice notes, personal grievances, roommate negotiations, and lighthearted teasing must **never** be transmitted to external servers, cloud databases, or third-party AI providers.
        - **No Company Data Leaks**: Trainees often discuss internal assessment hints, educator instructions, batch schedules, and proprietary training materials. Keeping all processing local ensures compliance with company privacy policies and non-disclosure agreements.
        - **Zero Analytics or Telemetry**: No tracking cookies, no Google Analytics, no third-party CDNs.

        #### 3. ⚡ Local Grounding Over Generic Cloud Hallucinations
        - Commercial cloud LLMs lack hyper-local context: they have no idea what *"JC multiplex movie token"*, *"65% FA cutoff"*, *"GEC Greek pillars biometric sprint"*, or *"ECC laundry token scarcity"* actually mean.
        - By fusing **local Ollama models** (`llama3`, `gemma2`) with our **structured local JSON campus dictionary**, this application provides culturally grounded, authentic translations that resonate with trainees.

        ---

        #### 💻 System Architecture Diagram
        ```
        +------------------------------------------------------------------------------------+
        |                         OFFLINE LOCALHOST PERIMETER                                |
        |                                                                                    |
        |   +-----------------------+                    +-------------------------------+   |
        |   |   Streamlit Frontend  |                    |      FastAPI Backend API      |   |
        |   |   (Port 8501)         | <----------------> |      (Port 8000)              |   |
        |   |   - Text Slang Input  |     Local HTTP     |   - Slang Translation Engine  |   |
        |   |   - Voice Note Upload |                    |   - Audio Waveform Processor  |   |
        |   |   - Lexicon Explorer  |                    |   - JSON Dictionary Storage   |   |
        |   +-----------------------+                    +-------------------------------+   |
        |                                                                |                   |
        |                                                                v                   |
        |   +------------------------------------+       +-------------------------------+   |
        |   |    Local Campus Context Layer      |       |      Ollama Local AI Engine   |   |
        |   |    (data/campus_dictionary.json)   | <---> |      (Port 11434)             |   |
        |   |    - 20+ Mysore DC Campus Terms    |       |      - Llama-3 / Gemma-2      |   |
        |   |    - Grounding Retrieval System    |       |      - 100% Offline Inference |   |
        |   +------------------------------------+       +-------------------------------+   |
        +------------------------------------------------------------------------------------+
        ```
        """
    )
