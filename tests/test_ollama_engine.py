"""
Unit tests for OllamaService and Offline Fallback Engine.
"""
from backend.ollama_service import ollama_service


def test_offline_translation_breakdown():
    text = "Macha JC chalo, FA mein scene contra ho gaya!"
    breakdown = ollama_service.translate(text)

    # Validate output format requirements
    assert breakdown.source_text == text
    assert len(breakdown.direct_meaning) > 5
    assert len(breakdown.vibe_and_tone) > 5
    assert len(breakdown.on_campus_context) > 5
    assert len(breakdown.cultural_nuances) >= 1
    assert "JC" in breakdown.matched_terms or "Macha" in breakdown.matched_terms or "Scene Contra" in breakdown.matched_terms
    assert breakdown.roommate_reply_suggestion is not None


def test_roommate_compromise_breakdown():
    text = "Roommate swalpa adjust maadi yaar, AC temperature 24 pe rakho."
    breakdown = ollama_service.translate(text)

    assert "Swalpa Adjust Maadi" in breakdown.matched_terms
    assert "adjust" in breakdown.direct_meaning.lower() or "kannada" in str(breakdown.cultural_nuances).lower()
