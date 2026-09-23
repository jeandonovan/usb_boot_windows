@echo off
setlocal
cd /d "%~dp0"
where powershell.exe >nul 2>&1 || (echo PowerShell est requis.&pause&exit /b 1)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0telecharger_windows.ps1"
if errorlevel 1 pause
