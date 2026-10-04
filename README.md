# 🏛️ DC Roommate Slang Bridge

> **Local-First Cultural Translator & Roommate Linguistic Bridge for Infosys Mysore DC Trainees**  
> *100% Offline • Zero External Cloud API Dependencies • Hostel Wi-Fi Resilient • Privacy Preserving*

---

## 📖 Overview

At the world-renowned **337-acre Infosys Development Centre (DC) in Mysuru, Karnataka**, thousands of fresh engineering recruits arrive from every corner of India — Delhi, Kerala, Tamil Nadu, Andhra Pradesh, Telangana, Maharashtra, West Bengal, and Karnataka. 

Roommates are paired across different linguistic backgrounds in the **Employee Care Centre (ECC)** hostels. Between running to **GEC 1** for the **9:15 AM biometric punch**, panicking over the **65% FA (Focus Assessment) cutoff**, hunting for unlocked **green campus cycles**, and grabbing butter masala dosas at the **JC multiplex food court**, communication can get delightfully lost in translation!

**DC Roommate Slang Bridge** is a full-stack, local-first web application that bridges this gap. It translates regional slang, hostel banter, and mess terminology into structured, actionable breakdowns grounded in genuine campus culture.

---

## 🎯 Key Features

1. **Responsive Streamlit Dashboard**:
   - Tailored specifically for Infosys Mysore trainees with a sleek campus aesthetic.
   - **Text Slang Translator**: Accepts phrases like *"Macha JC chalo, FA mein scene contra ho gaya aliya!"* with one-click quick-fill prompt chips.
   - **Voice Note Audio Bridge**: Upload `.wav`, `.mp3`, `.ogg`, or `.m4a` voice recordings or test with pre-packaged campus voice notes.
   - **Mysore DC Campus Lexicon**: Interactive dictionary explorer with live search, category filters, and an expandable form to contribute new slang directly to local storage.

2. **Standardized 3-Part Output Breakdown**:
   - 📘 **Direct Meaning / Translation**: Clear literal and conversational translation.
   - 🎭 **The Vibe / Tone**: Decodes the emotional subtext (e.g., panic, gentle roommate compromise, celebration).
   - 🏛️ **On-Campus Context**: Connects the phrase to specific Mysore DC realities (GEC Greek pillars, JC multiplex, ECC blocks, Re-FA panic, laundry tokens).
   - 🌐 **Cultural Nuances**: Highlights regional linguistic origin (Kannada, Malayalam, Hindi, Tamil, Telugu).
   - 💬 **Suggested Roommate Reply**: Contextual, witty response ready to copy and send back.

3. **Local AI Engine (Ollama Integration)**:
   - Uses the official `ollama` Python client to query locally hosted open-source models (defaulting to **Llama-3** or **Gemma-2**).
   - Enforces structured JSON output schema via Ollama's native JSON mode.
   - Includes an intelligent **Offline Heuristic Synthesizer**: if your Ollama daemon is offline or starting up, the application continues to run seamlessly using deterministic local dictionary grounding!

4. **Cultural Context Layer (`data/campus_dictionary.json`)**:
   - Structured JSON database of 20+ authentic campus terms categorized by Campus Landmarks, Academics (FP & FA), Hostel Living, and Regional Slang (Kannada, Malayalam, Tamil, Telugu, Hindi).
   - Dynamic boundary-aware matcher extracts all relevant campus terms from any sentence and injects them into the model's system prompt.

---

## 🛡️ Why an Open-Source Local Approach Matters

### 1. 📶 Hostel Wi-Fi Resilience & Network Throttling
- **Evening Peak Congestion**: In ECC hostel clusters housing 5,000+ trainees simultaneously streaming lectures or video calling home, hostel Wi-Fi experiences heavy packet loss and bandwidth throttling.
- **Enterprise Firewall Restrictions**: Infosys training networks strictly block external AI endpoints (e.g., OpenAI, Anthropic, external cloud gateways), unauthorized WebSockets, or non-standard ports.
- **True Offline Uptime**: By running the frontend (Streamlit `localhost:8501`), backend (FastAPI `localhost:8000`), and AI engine (Ollama `localhost:11434`) strictly on `127.0.0.1`, the app works with **zero active internet connection**. It works during complete router outages, in hostel basement labs, or on the train between Mysore and Bangalore.

### 2. 🔒 Absolute Privacy for Hostel Roommates
- **Confidential Roommate Conversations**: Trainees share twin-sharing rooms with strangers who quickly become close friends. Private voice notes, personal grievances, humorous room disputes, and lighthearted teasing must **never** be sent to cloud servers or third-party AI companies.
- **Zero Corporate Leakage**: Trainees frequently mention educator feedback, batch numbers, internal course codes, or mock assessment details. Running 100% locally guarantees strict compliance with corporate NDAs and non-disclosure policies.
- **Zero Telemetry or Trackers**: No third-party analytics, cookies, or cloud font CDNs.

### 3. ⚡ Local Grounding vs. Generic Cloud Hallucinations
- Generic cloud LLMs hallucinate when asked about *"JC Dosa"*, *"Re-FA cutoff"*, or *"ECC laundry token shortage"*.
- By anchoring local open-source models with our curated `campus_dictionary.json`, every response is grounded in authentic Mysore DC trainee culture.

---

## 📂 Complete Directory Structure

```
dcSla/
│
├── backend/
│   ├── __init__.py                 # Package marker
│   ├── config.py                   # Local paths, ports, and model configuration
│   ├── models.py                   # Pydantic schemas (Translation, Dictionary, Audio)
│   ├── dictionary_service.py       # JSON dictionary management, search, and context grounding
│   ├── ollama_service.py           # Local Ollama client integration & offline heuristic engine
│   ├── audio_service.py            # Local voice note parser & sample audio synthesizer
│   └── main.py                     # FastAPI application & REST API routes
│
├── frontend/
│   ├── __init__.py                 # Package marker
│   ├── styles.py                   # Mysore DC custom CSS theme (cards, badges, typography)
│   ├── components.py               # Reusable UI cards (3-part breakdown, hero banner, tags)
│   └── app.py                      # Interactive Streamlit dashboard application
│
├── data/
│   ├── campus_dictionary.json      # Structured Mysore DC slang & campus context database
│   └── sample_voice_notes/         # Pre-packaged sample voice notes (.wav + .txt metadata)
│
├── tests/
│   ├── __init__.py                 # Test package marker
│   ├── test_api.py                 # FastAPI REST endpoint integration tests
│   ├── test_dictionary.py          # Dictionary loading, searching, and term matching tests
│   └── test_ollama_engine.py       # Ollama integration and offline breakdown tests
│
├── scripts/
│   ├── run_app.bat                 # One-click Windows runner script
│   ├── run_app.ps1                 # PowerShell runner with Ollama health detection
│   └── run_app.sh                  # Linux / macOS shell runner script
│
├── uploads/                        # Local temporary storage for voice notes
│   └── .gitkeep
├── requirements.txt                # Pinned Python dependencies
├── .gitignore                      # Git exclusion rules
└── README.md                       # Complete documentation & privacy manifesto
```

---

## 🚀 Quickstart Guide

### Prerequisites
- **Python**: 3.10+ installed
- *(Optional for Local LLM Inference)*: [Ollama](https://ollama.com/) installed and running locally with `llama3` or `gemma2`:
  ```bash
  ollama run llama3
  # or
  ollama run gemma2
  ```
  *(Note: If Ollama is not installed or running, the application automatically uses its built-in offline grounding engine with 100% functionality!)*

### Step 1: Clone and Install Dependencies
```bash
git clone <repo-url> dcSla
cd dcSla

pip install -r requirements.txt
```

### Step 2: Run the Application

#### Option A: One-Click Runner (Windows PowerShell)
```powershell
.\scripts\run_app.ps1
```

#### Option B: One-Click Runner (Windows CMD Batch)
```cmd
scripts\run_app.bat
```

#### Option C: Manual Launch (Two Terminals)

**Terminal 1 — FastAPI Backend:**
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 — Streamlit Frontend:**
```bash
python -m streamlit run frontend/app.py --server.port 8501
```

Open your browser to: **`http://localhost:8501`**

---

## 🔌 FastAPI REST API Reference

The backend provides clean REST endpoints accessible at `http://127.0.0.1:8000`:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Returns Ollama daemon connection, active model, and term count |
| `POST` | `/api/translate` | Accepts slang text and returns 3-part structured breakdown |
| `POST` | `/api/transcribe` | Accepts voice note audio file and returns transcript + breakdown |
| `GET` | `/api/dictionary` | Queries campus dictionary with search and category filtering |
| `POST` | `/api/dictionary` | Adds a new campus term and persists it to local JSON |
| `GET` | `/api/models` | Lists local Ollama models detected on system |
| `GET` | `/api/sample-audio` | Returns pre-packaged test audio samples |

Interactive Swagger documentation is available offline at `http://127.0.0.1:8000/docs`.

---

## 🧪 Running the Test Suite

Run the full automated pytest suite:
```bash
python -m pytest tests/ -v
```

All 12 unit and integration tests validate:
- ✅ Health endpoint and Ollama connection detection
- ✅ Slang translation and 3-part breakdown format
- ✅ Dictionary fuzzy search and multi-term extraction
- ✅ Voice note audio synthesis and transcription processing
- ✅ Local offline heuristic fallback resilience

---

## 🎓 Campus Slang Sample Cheat Sheet

| Phrase | Region / Language | Trainee Context |
| :--- | :--- | :--- |
| *"Macha JC chalo, FA mein scene contra ho gaya aliya!"* | Kannada + Malayalam + Hindi | Trainee asking roommate to head to JC food court after an exam disaster. |
| *"Roommate swalpa adjust maadi yaar, AC temperature 24 pe rakho."* | Kannada + Hindi | Classic ECC hostel room negotiation regarding AC thermostat settings. |
| *"Who took my green cycle? 9:15 punch miss ho jayega!"* | Campus Lingo | Frantic morning sprint across GEC lawns in formal shoes. |
| *"Educator semma gaandu aayitaaru, 4th test case fail."* | Tamil + Campus Lingo | Coding lab stress when an assessment solution fails hidden test cases. |
| *"Mama Oasis lo parotta thindama, dhimak kharab aypoyindi."* | Telugu + Campus Lingo | Overwhelmed trainee seeking comfort food at Oasis mess after long lab hours. |
| *"FA1 mein 92 marks phod diya! Weekend multiplex sorted."* | Hindi + Campus Lingo | Smashed the assessment; ready for free weekend movie screenings at JC multiplex. |

---

## 📜 License
Open-source under the MIT License. Built for trainees and roommates everywhere.
