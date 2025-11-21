# Voice Agent Launcher - Day 1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AI Voice Agent - Service Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "You need to run THREE services in separate terminals:" -ForegroundColor Yellow
Write-Host ""

Write-Host "Current Terminal - Choose a service to run:" -ForegroundColor White
Write-Host ""
Write-Host "1. LiveKit Server (run first)" -ForegroundColor Green
Write-Host "2. Backend Agent (run after LiveKit server starts)" -ForegroundColor Green
Write-Host "3. Frontend (run after backend agent starts)" -ForegroundColor Green
Write-Host "4. Show all commands (copy/paste to run in separate terminals)" -ForegroundColor Cyan
Write-Host "5. Exit" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter your choice (1-5)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Starting LiveKit Server..." -ForegroundColor Green
        Write-Host "Press Ctrl+C to stop when done" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "After this starts, open TWO MORE terminals and run:" -ForegroundColor Cyan
        Write-Host "  Terminal 2: .\start-services.ps1  (choose option 2)" -ForegroundColor White
        Write-Host "  Terminal 3: .\start-services.ps1  (choose option 3)" -ForegroundColor White
        Write-Host ""
        Start-Sleep -Seconds 2
        livekit-server --dev
    }
    "2" {
        Write-Host ""
        Write-Host "Starting Backend Agent..." -ForegroundColor Green
        Write-Host "Press Ctrl+C to stop when done" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Make sure LiveKit Server is running in another terminal!" -ForegroundColor Yellow
        Write-Host ""
        Start-Sleep -Seconds 2
        Set-Location backend
        uv run python src/agent.py dev
    }
    "3" {
        Write-Host ""
        Write-Host "Starting Frontend..." -ForegroundColor Green
        Write-Host "Press Ctrl+C to stop when done" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Make sure LiveKit Server and Backend are running!" -ForegroundColor Yellow
        Write-Host ""
        Start-Sleep -Seconds 2
        Set-Location frontend
        pnpm dev
    }
    "4" {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "  Copy these commands to 3 terminals" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Terminal 1 (LiveKit Server):" -ForegroundColor Green
        Write-Host "  livekit-server --dev" -ForegroundColor White
        Write-Host ""
        Write-Host "Terminal 2 (Backend Agent):" -ForegroundColor Green
        Write-Host "  cd d:\Projects_External\ten-days-of-voice-agents-2025\backend" -ForegroundColor White
        Write-Host "  uv run python src/agent.py dev" -ForegroundColor White
        Write-Host ""
        Write-Host "Terminal 3 (Frontend):" -ForegroundColor Green
        Write-Host "  cd d:\Projects_External\ten-days-of-voice-agents-2025\frontend" -ForegroundColor White
        Write-Host "  pnpm dev" -ForegroundColor White
        Write-Host ""
        Write-Host "Then open: http://localhost:3000" -ForegroundColor Cyan
        Write-Host ""
        pause
    }
    "5" {
        Write-Host "Goodbye!" -ForegroundColor Cyan
        exit 0
    }
    default {
        Write-Host "Invalid choice. Run the script again." -ForegroundColor Red
    }
}
