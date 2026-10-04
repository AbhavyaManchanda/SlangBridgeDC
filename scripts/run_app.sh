#!/usr/bin/env bash
set -e

echo "======================================================="
echo "  DC Roommate Slang Bridge - Infosys Mysore DC"
echo "  100% Local-First Offline Runner"
echo "======================================================="

# Trap to kill backend on exit
trap 'kill $(jobs -p) 2>/dev/null || true' EXIT

echo "Starting FastAPI Backend on http://127.0.0.1:8000 ..."
python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 &

sleep 2

echo "Starting Streamlit Frontend on http://127.0.0.1:8501 ..."
python3 -m streamlit run frontend/app.py --server.port 8501
