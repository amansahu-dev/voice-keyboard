# Voice Keyboard Assistant

A voice-controlled keyboard assistant that allows you to control your computer using voice commands.

## Requirements
- Windows 10 or later
- Python 3.11 or later
- Working microphone

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

2. Install PyAudio (Windows):
- Download the appropriate PyAudio wheel for your Python version from:
  https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
  - For Python 3.11: `PyAudio‑0.2.13‑cp311‑cp311‑win_amd64.whl`
  - For Python 3.10: `PyAudio‑0.2.13‑cp310‑cp310‑win_amd64.whl`

```bash
# Replace XX with your Python version (e.g., 311 for Python 3.11)
pip install PyAudio‑0.2.13‑cpXXX‑cpXXX‑win_amd64.whl
```

3. Install other dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
streamlit run voice_keyboard.py
```

2. Click "Start Listening" to begin voice recognition
3. Speak commands naturally
4. Click "Stop" to stop listening

## Available Commands

### Basic Navigation
- "enter", "next line", "new line"
- "space", "tab"
- "backspace", "delete"
- "escape"

### Word Operations
- "remove word", "delete word"
- "capital [word]" (capitalizes next word)
- "all caps" (toggles caps lock)

### Navigation
- "go left", "go right", "go up", "go down"
- "word left", "word right"
- "go to start", "go to end"
- "line start", "line end"

### Selection
- "select word", "select line"
- "select next word", "select previous word"
- "select up", "select down"
- "select all"

### Copy/Paste
- "copy", "paste", "cut"
- "copy line", "cut line"
- "copy word", "cut word"
- "undo", "redo"

### Symbols
- Quotes: "double quote", "single quote"
- Brackets: "open bracket", "close bracket", "square bracket"
- Punctuation: "comma", "period", "semicolon"
- Math: "plus", "minus", "equals"
- Special: "underscore", "at sign", "hash"

## Troubleshooting

1. If microphone isn't working:
   - Check Windows microphone permissions
   - Set your microphone as the default recording device
   - Try running the application as administrator

2. If keyboard commands aren't working:
   - Ensure the application has necessary permissions
   - Try running as administrator
   - Check if any antivirus is blocking PyAutoGUI

3. Common Issues:
   - "PyAudio not found": Follow installation steps for PyAudio
   - "Microphone not detected": Check Windows sound settings
   - "Command not recognized": Speak clearly and check command list 