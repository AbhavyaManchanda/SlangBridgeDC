"""
FastAPI Backend Application for DC Roommate Slang Bridge.
Exposes clean REST endpoints for local slang translation, voice note audio processing,
and campus dictionary management. Runs 100% offline.
"""
import logging
from typing import List, Optional

from fastapi import FastAPI, File, HTTPException, Query, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.audio_service import audio_service
from backend.config import DEFAULT_OLLAMA_MODEL, OLLAMA_HOST
from backend.dictionary_service import dictionary_service
from backend.models import (
    AddTermRequest,
    AudioTranscriptionResponse,
    DictionaryResponse,
    DictionaryTerm,
    HealthStatus,
    TranslationBreakdown,
    TranslationRequest,
)
from backend.ollama_service import ollama_service

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("dc_slang_bridge")

# FastAPI App
app = FastAPI(
    title="DC Roommate Slang Bridge API",
    description="Local-first API for Infosys Mysore DC slang translation, cultural context grounding, and voice note transcription.",
    version="1.0.0",
)

# Enable CORS for local Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthStatus, summary="Check system health and Ollama status")
def health_check():
    """Returns local runtime status, Ollama daemon reachability, and dictionary stats."""
    is_connected, available_models = ollama_service.check_connection()
    selected_model, _ = ollama_service.get_preferred_model()
    terms_count = len(dictionary_service.get_all_terms())

    mode = "Ollama Local AI (Active)" if is_connected else "Offline Local Heuristic & Grounding Engine"
    return HealthStatus(
        status="healthy",
        ollama_connected=is_connected,
        ollama_host=OLLAMA_HOST,
        available_models=available_models,
        selected_model=selected_model,
        dictionary_terms_count=terms_count,
        mode=mode,
    )


@app.post("/api/translate", response_model=TranslationBreakdown, summary="Translate and explain campus slang")
def translate_slang(request: TranslationRequest):
    """
    Translates regional slang or hostel messages into:
    1. Direct Meaning / Translation
    2. The Vibe / Tone
    3. On-Campus Context (JC, GEC, ECC, FA, etc.)
    """
    if not request.text or not request.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Input text cannot be empty.",
        )

    try:
        breakdown = ollama_service.translate(
            text=request.text.strip(),
            model_name=request.model_name,
            context_hint=request.context_hint,
        )
        return breakdown
    except Exception as e:
        logger.error("Translation error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation failed: {str(e)}",
        )


@app.post("/api/transcribe", response_model=AudioTranscriptionResponse, summary="Transcribe and translate voice notes")
async def transcribe_voice_note(
    file: UploadFile = File(...),
    context_hint: Optional[str] = Query(None, description="Optional extra context"),
    model_name: Optional[str] = Query(None, description="Ollama model to use"),
):
    """
    Accepts an uploaded voice note audio file (.wav, .mp3, .ogg, .m4a),
    transcribes it offline, and runs it through the slang grounding engine.
    """
    try:
        content = await file.read()
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty.",
            )

        filename = file.filename or "recording.wav"
        result = audio_service.process_audio(
            file_bytes=content,
            filename=filename,
            context_hint=context_hint,
            model_name=model_name,
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Audio processing failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Voice note processing error: {str(e)}",
        )


@app.get("/api/dictionary", summary="List and search campus dictionary terms")
def get_dictionary(
    category: Optional[str] = Query(None, description="Filter by category ID"),
    search: Optional[str] = Query(None, description="Search query"),
):
    """Returns Infosys Mysore terms, definitions, and categories."""
    terms = dictionary_service.search_terms(query=search or "", category_id=category)
    categories = dictionary_service.get_categories()
    return {
        "total_terms": len(terms),
        "categories": categories,
        "terms": [t.model_dump() for t in terms],
    }


@app.post("/api/dictionary", response_model=DictionaryTerm, status_code=status.HTTP_201_CREATED, summary="Add custom campus slang")
def add_dictionary_term(request: AddTermRequest):
    """Allows trainees to add a new hostel slang or mess term directly to the local dictionary."""
    try:
        new_term = dictionary_service.add_term(request)
        return new_term
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error("Failed to add term: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/api/sample-audio", summary="List pre-packaged sample voice notes")
def get_sample_voice_notes():
    """Returns pre-packaged audio samples for immediate offline testing in the UI."""
    return audio_service.get_sample_voice_notes()


@app.get("/api/models", summary="List available local Ollama models")
def list_models():
    """Lists locally installed Ollama models and connection state."""
    is_connected, available = ollama_service.check_connection()
    return {
        "connected": is_connected,
        "host": OLLAMA_HOST,
        "default_model": DEFAULT_OLLAMA_MODEL,
        "available_models": available,
    }


if __name__ == "__main__":
    import uvicorn
    from backend.config import BACKEND_HOST, BACKEND_PORT

    uvicorn.run("backend.main:app", host=BACKEND_HOST, port=BACKEND_PORT, reload=True)
