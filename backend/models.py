"""
Pydantic data models and schemas for DC Roommate Slang Bridge.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class TranslationRequest(BaseModel):
    """Payload for slang translation and cultural grounding."""
    text: str = Field(..., min_length=1, description="Slang, voice transcript, or hostel message")
    model_name: Optional[str] = Field(None, description="Ollama model to use (defaults to system config)")
    context_hint: Optional[str] = Field(None, description="Optional extra context (e.g., 'JC food court', 'FA exam')")


class TranslationBreakdown(BaseModel):
    """Structured breakdown required by specification: Direct Meaning, Vibe/Tone, Campus Context."""
    source_text: str
    direct_meaning: str = Field(..., description="Literal or contextual translation")
    vibe_and_tone: str = Field(..., description="The attitude, emotion, stress level, or banter vibe")
    on_campus_context: str = Field(..., description="Infosys Mysore specific context (JC, GEC, ECC, FA, etc.)")
    cultural_nuances: List[str] = Field(default_factory=list, description="Regional or cross-state linguistic nuances")
    matched_terms: List[str] = Field(default_factory=list, description="Campus dictionary terms detected in input")
    model_used: str = Field(..., description="Model or engine that generated this breakdown")
    is_offline_grounded: bool = Field(True, description="True if grounded via local dictionary")
    roommate_reply_suggestion: Optional[str] = Field(
        None, description="A witty or helpful suggested reply for the trainee to send their roommate"
    )
    formatted_markdown: Optional[str] = Field(
        None, description="Clean Markdown representation of the breakdown without HTML div tags"
    )

    def to_markdown(self) -> str:
        """Generates clean Markdown formatting without HTML div tags for native Streamlit rendering."""
        if self.formatted_markdown:
            return self.formatted_markdown

        terms_badges = " ".join([f"`{t}`" for t in self.matched_terms]) if self.matched_terms else "`Conversational Campus Lingo`"
        nuances_bullets = "\n".join([f"- {item}" for item in self.cultural_nuances]) if self.cultural_nuances else "- Authentic cross-state roommate communication"
        
        reply_block = ""
        if self.roommate_reply_suggestion:
            reply_block = f"#### 💬 Suggested Roommate Response\n> *\"{self.roommate_reply_suggestion}\"*\n\n"

        md = (
            f"### 📘 Direct Meaning / Translation\n"
            f"> {self.direct_meaning}\n\n"
            f"### 🎭 The Vibe & Tone\n"
            f"**{self.vibe_and_tone}**\n\n"
            f"### 🏛️ On-Campus Context (JC, GEC, or Hostel Life)\n"
            f"{self.on_campus_context}\n\n"
            f"---\n\n"
            f"{reply_block}"
            f"#### 🌐 Cultural & Linguistic Nuances\n"
            f"{nuances_bullets}\n\n"
            f"#### 🏷️ Detected Campus Terms\n"
            f"{terms_badges}\n\n"
            f"---\n"
            f"*⚙️ **Engine:** {self.model_used}  |  🛡️ **Grounding:** Local Campus Dictionary  |  🔒 **100% Offline & Private***\n"
        )
        return md


class DictionaryTerm(BaseModel):
    """Schema for a single Infosys Mysore campus dictionary entry."""
    term: str
    aliases: List[str] = Field(default_factory=list)
    category: str
    languages: List[str] = Field(default_factory=list)
    meaning: str
    vibe: str
    campus_context: str
    example_usage: str
    keywords: List[str] = Field(default_factory=list)


class DictionaryResponse(BaseModel):
    """Schema for dictionary query response."""
    total_terms: int
    categories: List[dict]
    terms: List[DictionaryTerm]


class AddTermRequest(BaseModel):
    """Payload for adding a new campus slang/mess term to local dictionary."""
    term: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    languages: List[str] = Field(default_factory=lambda: ["Campus Lingo"])
    meaning: str = Field(..., min_length=3)
    vibe: str = Field(..., min_length=3)
    campus_context: str = Field(..., min_length=5)
    example_usage: str = Field(..., min_length=5)
    aliases: Optional[List[str]] = Field(default_factory=list)


class AudioTranscriptionResponse(BaseModel):
    """Response returned when an audio voice note is transcribed and translated."""
    file_name: str
    audio_format: str
    duration_seconds: float
    transcribed_text: str
    engine_used: str
    confidence: float
    breakdown: Optional[TranslationBreakdown] = None


class HealthStatus(BaseModel):
    """Application health and local runtime status."""
    status: str
    ollama_connected: bool
    ollama_host: str
    available_models: List[str]
    selected_model: str
    dictionary_terms_count: int
    mode: str
    version: str = "1.0.0"
