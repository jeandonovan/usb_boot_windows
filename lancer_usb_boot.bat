@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1 && set "PY=py" || set "PY=python"
%PY% --version >nul 2>&1
if errorlevel 1 (
  echo Python est requis. Installez-le depuis https://www.python.org/downloads/windows/ en cochant ^"Add Python to PATH^".
  pause
  exit /b 1
)
net session >nul 2>&1
if errorlevel 1 (
  echo Demande des droits administrateur...
  powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
  exit /b
)
%PY% "%~dp0usb_boot_windows.py"
if errorlevel 1 pause
