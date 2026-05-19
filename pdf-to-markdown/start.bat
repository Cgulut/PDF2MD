@echo off
cd /d "%~dp0"

set "VENV_PATH=C:\Users\%USERNAME%\pdf2md_venv"

:: ── 1. Check for Python 3.10+ ────────────────────────────────────────────────
echo Checking Python...
python -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
if not errorlevel 1 goto :setup_venv

echo Python 3.10+ not found. Installing via winget...
where winget >nul 2>&1
if errorlevel 1 (
    echo.
    echo  ERROR: winget is not available on this machine.
    echo  Please install Python 3.10+ manually from:
    echo    https://www.python.org/downloads/
    echo  Check "Add Python to PATH" during installation, then run this file again.
    echo.
    pause
    exit /b 1
)

winget install --id Python.Python.3.13 --source winget --silent --accept-package-agreements --accept-source-agreements
if errorlevel 1 (
    echo.
    echo  ERROR: Python installation failed.
    echo  Please install Python 3.10+ manually from:
    echo    https://www.python.org/downloads/
    echo  Check "Add Python to PATH" during installation, then run this file again.
    echo.
    pause
    exit /b 1
)

:: Refresh PATH from registry so the newly installed Python is visible
for /f "skip=2 tokens=1,2,*" %%a in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set "USR_PATH=%%c"
for /f "skip=2 tokens=1,2,*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul') do set "SYS_PATH=%%c"
set "PATH=%SYS_PATH%;%USR_PATH%"

python -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
if errorlevel 1 (
    echo.
    echo  Python installed successfully.
    echo  Please close this window and run start.bat again to complete setup.
    echo.
    pause
    exit /b 0
)

echo Python installed successfully.

:: ── 2. Create venv and install dependencies ───────────────────────────────────
:setup_venv
if not exist "%VENV_PATH%\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv "%VENV_PATH%"
)

call "%VENV_PATH%\Scripts\activate.bat"

if not exist "%VENV_PATH%\Scripts\streamlit.exe" (
    echo Installing dependencies - this may take several minutes...
    pip install -r requirements.txt
)

:: ── 3. Launch app ─────────────────────────────────────────────────────────────
echo.
echo Starting PDF to Markdown converter...
echo Open http://localhost:8501 in your browser.
echo Press Ctrl+C to stop.
echo.
streamlit run app.py
