@echo off
cd /d "%~dp0"

set VENV_PATH=C:\Users\Lenovo 3\pdf2md_venv

if not exist "%VENV_PATH%\Scripts\activate.bat" (
    echo First-time setup: creating virtual environment...
    python -m venv "%VENV_PATH%"
)

call "%VENV_PATH%\Scripts\activate.bat"

if not exist "%VENV_PATH%\Scripts\streamlit.exe" (
    echo Installing dependencies - this may take several minutes...
    pip install -r requirements.txt
)

echo Starting PDF to Markdown converter...
echo Open http://localhost:8501 in your browser.
echo Press Ctrl+C to stop.
streamlit run app.py
