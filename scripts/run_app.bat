@echo off
echo =======================================================
echo   DC Roommate Slang Bridge - Infosys Mysore DC
echo   100%% Local-First Offline Runner
echo =======================================================

echo.
echo Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "DC Slang Backend" python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

timeout /t 2 /nobreak >nul

echo Starting Streamlit Frontend on http://127.0.0.1:8501 ...
python -m streamlit run frontend/app.py --server.port 8501 --server.headless false

pause
