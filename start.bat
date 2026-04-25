@echo off
REM Windows double-click launcher for the Tally Dashboard.
REM Delegates to start.ps1 in PowerShell (bypasses execution policy for this run only).
setlocal
set SCRIPTDIR=%~dp0
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPTDIR%start.ps1"
pause
