@echo off
echo Starting Voice Keyboard Assistant...
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate
)

echo.
echo Starting application...
echo.
streamlit run voice_keyboard.py

pause 