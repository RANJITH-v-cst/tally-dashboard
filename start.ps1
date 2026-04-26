# One-command local start for the Tally Dashboard on Windows PowerShell.
#   .\start.ps1
# Requires: Python 3.12+, Node 22+. Installs uv on first run.

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Definition

function Ensure-Uv {
    if (Get-Command uv -ErrorAction SilentlyContinue) { return }
    Write-Host "[setup] Installing uv (Python package manager)..." -ForegroundColor Cyan
    irm https://astral.sh/uv/install.ps1 | iex
    $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
}

Ensure-Uv

Write-Host "[setup] Syncing backend deps..." -ForegroundColor Cyan
Push-Location "$Root\backend"
uv sync --quiet
Pop-Location

Write-Host "[setup] Installing frontend deps..." -ForegroundColor Cyan
Push-Location "$Root\frontend"
if (-not (Test-Path node_modules)) { npm install --silent }
Pop-Location

$TallyUrl = if ($env:TALLY_URL) { $env:TALLY_URL } else { "http://localhost:9000" }

Write-Host ""
Write-Host "[start] Tally URL:   $TallyUrl"
Write-Host "[start] Backend:     http://localhost:8787  (docs at /docs)"
Write-Host "[start] Dashboard:   http://localhost:5173"
Write-Host ""
Write-Host "Press Ctrl+C in either window to stop." -ForegroundColor Yellow
Write-Host ""

# Launch backend and frontend in separate PowerShell windows so you can
# see logs from each. Close either window (or Ctrl+C) to stop it.
$backendCmd = "cd `"$Root\backend`"; `$env:TALLY_URL='$TallyUrl'; uv run uvicorn app.main:app --host 127.0.0.1 --port 8787"
$frontendCmd = "cd `"$Root\frontend`"; npm run dev -- --host"

Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", $backendCmd
Start-Sleep -Seconds 2
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", $frontendCmd
Start-Sleep -Seconds 3

Write-Host "Opening http://localhost:5173 ..." -ForegroundColor Green
Start-Process "http://localhost:5173"
