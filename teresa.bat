@echo off
REM ============================================================================
REM teresa.bat — double-click launcher for teresa GUI
REM Place this in the repo root next to run.ps1 and teresa_gui.py
REM Optionally create a shortcut to this .bat on Desktop.
REM ============================================================================

cd /d "%~dp0"

REM Check Python availability
where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: python not found in PATH.
    echo Install Python 3.10+ and try again.
    pause
    exit /b 1
)

REM Check PyQt6
python -c "import PyQt6" 2>nul
if errorlevel 1 (
    echo PyQt6 not installed. Installing now...
    python -m pip install PyQt6
    if errorlevel 1 (
        echo ERROR: pip install PyQt6 failed.
        pause
        exit /b 1
    )
)

REM Launch GUI (no console window — uses pythonw)
start "" pythonw "%~dp0teresa_gui.py"
exit /b 0
