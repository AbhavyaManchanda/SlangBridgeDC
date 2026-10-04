# DC Roommate Slang Bridge - PowerShell Launch Script
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "  DC Roommate Slang Bridge - Infosys Mysore DC" -ForegroundColor Yellow
Write-Host "  100% Local-First Offline Runner" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Cyan

# Check if Ollama daemon is reachable
try {
    $ollamaCheck = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -Method Get -TimeoutSec 2 -ErrorAction SilentlyContinue
    Write-Host "[OK] Local Ollama service detected running at http://127.0.0.1:11434" -ForegroundColor Green
} catch {
    Write-Host "[INFO] Ollama daemon is currently not running at http://127.0.0.1:11434." -ForegroundColor Yellow
    Write-Host "       The application will run seamlessly using its built-in offline grounding engine." -ForegroundColor Yellow
    Write-Host "       (To enable full LLM inference, run 'ollama run llama3' in a separate terminal)" -ForegroundColor Gray
}

Write-Host "`nStarting FastAPI Backend in the background..." -ForegroundColor Cyan
$backendProcess = Start-Process python -ArgumentList "-m uvicorn backend.main:app --host 127.0.0.1 --port 8000" -PassThru -NoNewWindow

Start-Sleep -Seconds 2

Write-Host "Starting Streamlit Frontend on http://127.0.0.1:8501..." -ForegroundColor Cyan
try {
    python -m streamlit run frontend/app.py --server.port 8501
} finally {
    if ($backendProcess -and -not $backendProcess.HasExited) {
        Write-Host "Stopping FastAPI backend..." -ForegroundColor Gray
        Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
    }
}
