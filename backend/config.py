"""
Configuration settings for DC Roommate Slang Bridge.
Designed for 100% offline, local-first execution.
"""
import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DICTIONARY_PATH = DATA_DIR / "campus_dictionary.json"
SAMPLES_DIR = DATA_DIR / "sample_voice_notes"
UPLOAD_DIR = BASE_DIR / "uploads"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Server Configuration
BACKEND_HOST = os.getenv("DC_BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = int(os.getenv("DC_BACKEND_PORT", "8000"))
BACKEND_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"

# Streamlit Configuration
STREAMLIT_PORT = int(os.getenv("DC_STREAMLIT_PORT", "8501"))

# Ollama Local Configuration
# Default to standard local Ollama port; zero cloud dependencies
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
DEFAULT_OLLAMA_MODEL = os.getenv("DC_OLLAMA_MODEL", "llama3")
FALLBACK_OLLAMA_MODELS = ["llama3", "gemma2", "llama3.2", "mistral", "phi3", "qwen2"]

# Cultural Prompt System Configuration
CAMPUS_NAME = "Infosys Development Centre (DC) Mysore"
ACADEMIC_ZONES = ["GEC 1", "GEC 2", "ILI", "Heritage Building"]
FOOD_ZONES = ["JC Multiplex", "Fiesta", "Oasis", "Floating Restaurant", "Maggi Points"]
RESIDENTIAL_ZONES = ["ECC Hostels (Blocks 1-90+)", "Sports Complex", "Cycle Stands"]
