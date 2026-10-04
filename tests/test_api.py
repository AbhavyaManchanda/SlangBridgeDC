"""
API Integration tests for DC Roommate Slang Bridge.
"""
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "dictionary_terms_count" in data
    assert data["dictionary_terms_count"] >= 20


def test_translate_api():
    payload = {
        "text": "Macha GEC punch maarke direct JC mein milte hain",
        "context_hint": "Evening after lab",
    }
    response = client.post("/api/translate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "direct_meaning" in data
    assert "vibe_and_tone" in data
    assert "on_campus_context" in data
    assert "JC" in data["matched_terms"] or "Macha" in data["matched_terms"]


def test_dictionary_endpoints():
    response = client.get("/api/dictionary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_terms"] >= 20
    assert len(data["categories"]) >= 5


def test_sample_audio_endpoint():
    response = client.get("/api/sample-audio")
    assert response.status_code == 200
    samples = response.json()
    assert len(samples) >= 1
    assert "filename" in samples[0]


def test_transcribe_sample_wav():
    # Test uploading one of our synthesized sample files
    response = client.get("/api/sample-audio")
    samples = response.json()
    sample_file_path = samples[0]["path"]

    with open(sample_file_path, "rb") as f:
        file_bytes = f.read()

    files = {"file": (samples[0]["filename"], file_bytes, "audio/wav")}
    response = client.post("/api/transcribe", files=files)
    assert response.status_code == 200
    result = response.json()
    assert "transcribed_text" in result
    assert result["breakdown"] is not None
    assert "direct_meaning" in result["breakdown"]
