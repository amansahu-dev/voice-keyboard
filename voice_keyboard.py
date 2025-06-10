import streamlit as st
import time
import speech_recognition as sr
import pyttsx3
import pyautogui
import threading
import re

# Configure the application
st.set_page_config(
    page_title="Voice Keyboard Assistant",
    page_icon="🎤",
    layout="wide"
)

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# Initialize the recognizer
r = sr.Recognizer()

# Configure PyAutoGUI
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

# Command mappings
SPECIAL_KEYS = {
    'enter': 'enter',
    'next line': 'enter',
    'new line': 'enter',
    'space': 'space',
    'tab': 'tab',
    'backspace': 'backspace',
    'delete': 'delete',
    'escape': 'esc',
}

NAVIGATION_KEYS = {
    'go left': 'left',
    'go right': 'right',
    'go up': 'up',
    'go down': 'down',
    'word left': ['ctrl', 'left'],
    'word right': ['ctrl', 'right'],
    'go to start': 'home',
    'go to end': 'end',
    'line start': 'home',
    'line end': 'end',
}

SELECTION_KEYS = {
    'select all': ['ctrl', 'a'],
    'select word': ['ctrl', 'shift', 'right'],
    'select line': ['home', 'shift', 'end'],
    'select next word': ['ctrl', 'shift', 'right'],
    'select previous word': ['ctrl', 'shift', 'left'],
    'select up': ['shift', 'up'],
    'select down': ['shift', 'down'],
}

EDIT_KEYS = {
    'copy': ['ctrl', 'c'],
    'paste': ['ctrl', 'v'],
    'cut': ['ctrl', 'x'],
    'copy line': ['home', 'shift', 'end', 'ctrl', 'c'],
    'cut line': ['home', 'shift', 'end', 'ctrl', 'x'],
    'copy word': ['ctrl', 'shift', 'right', 'ctrl', 'c'],
    'cut word': ['ctrl', 'shift', 'right', 'ctrl', 'x'],
    'undo': ['ctrl', 'z'],
    'redo': ['ctrl', 'y'],
}

SYMBOLS = {
    'double quote': '"',
    'single quote': "'",
    'open bracket': '(',
    'close bracket': ')',
    'square bracket': '[',
    'close square bracket': ']',
    'comma': ',',
    'period': '.',
    'semicolon': ';',
    'plus': '+',
    'minus': '-',
    'equals': '=',
    'underscore': '_',
    'at sign': '@',
    'hash': '#',
}

def speak(text):
    """Text-to-speech output"""
    engine.say(text)
    engine.runAndWait()

def process_command(command):
    """Process voice commands and execute corresponding actions"""
    command = command.lower().strip()
    
    # Handle special keys
    if command in SPECIAL_KEYS:
        pyautogui.press(SPECIAL_KEYS[command])
        return f"Pressed {command}"
        
    # Handle navigation
    if command in NAVIGATION_KEYS:
        keys = NAVIGATION_KEYS[command]
        if isinstance(keys, list):
            pyautogui.hotkey(*keys)
        else:
            pyautogui.press(keys)
        return f"Executed {command}"
        
    # Handle selection
    if command in SELECTION_KEYS:
        keys = SELECTION_KEYS[command]
        pyautogui.hotkey(*keys)
        return f"Selected {command}"
        
    # Handle edit commands
    if command in EDIT_KEYS:
        keys = EDIT_KEYS[command]
        pyautogui.hotkey(*keys)
        return f"Executed {command}"
        
    # Handle symbols
    if command in SYMBOLS:
        pyautogui.write(SYMBOLS[command])
        return f"Typed {command}"
        
    # Handle capitalization
    if command.startswith('capital '):
        word = command[8:]  # Remove 'capital ' prefix
        pyautogui.write(word.capitalize())
        return f"Capitalized and typed: {word}"
        
    # Handle all caps
    if command == 'all caps':
        pyautogui.hotkey('capslock')
        return "Toggled caps lock"
        
    # Handle word deletion
    if command in ['remove word', 'delete word']:
        pyautogui.hotkey('ctrl', 'shift', 'right')
        pyautogui.press('delete')
        return "Deleted word"
        
    # Default: type the command as regular text
    pyautogui.write(command)
    return f"Typed: {command}"

def listen_for_commands():
    """Listen for voice input and process commands"""
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        while st.session_state.listening:
            try:
                audio = r.listen(source, timeout=1, phrase_time_limit=5)
                text = r.recognize_google(audio).lower()
                if text:
                    result = process_command(text)
                    st.session_state.last_command = result
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except sr.RequestError:
                st.error("Could not connect to speech recognition service")
                break
            except Exception as e:
                st.error(f"Error: {str(e)}")
                break

def main():
    st.title("Voice Keyboard Assistant 🎤")
    
    # Initialize session state
    if 'listening' not in st.session_state:
        st.session_state.listening = False
    if 'last_command' not in st.session_state:
        st.session_state.last_command = ""
    
    # Create tabs
    tab1, tab2 = st.tabs(["Main", "Help"])
    
    with tab1:
        # Add test textbox at the top
        st.text_area("Test your voice commands here:", height=200, key="test_area")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if not st.session_state.listening:
                if st.button("Start Listening"):
                    st.session_state.listening = True
                    thread = threading.Thread(target=listen_for_commands)
                    thread.start()
            else:
                if st.button("Stop"):
                    st.session_state.listening = False
            
            status = "🎤 Listening..." if st.session_state.listening else "🔇 Not listening"
            st.write(f"Status: {status}")
            
            if st.session_state.last_command:
                st.write(f"Last action: {st.session_state.last_command}")
        
        with col2:
            st.markdown("""
            ### Quick Tips
            1. Speak clearly and naturally
            2. Use commands like "capital [word]" for capitalization
            3. Say "enter" or "next line" for new lines
            4. Use navigation commands like "go left", "go right"
            5. Try selection commands like "select word", "select line"
            """)
    
    with tab2:
        st.markdown("""
        ### Available Commands
        
        #### Basic Navigation
        - "enter", "next line", "new line"
        - "space", "tab"
        - "backspace", "delete"
        - "escape"
        
        #### Word Operations
        - "remove word", "delete word"
        - "capital [word]" (capitalizes next word)
        - "all caps" (toggles caps lock)
        
        #### Navigation
        - "go left", "go right", "go up", "go down"
        - "word left", "word right"
        - "go to start", "go to end"
        - "line start", "line end"
        
        #### Selection
        - "select word", "select line"
        - "select next word", "select previous word"
        - "select up", "select down"
        - "select all"
        
        #### Copy/Paste
        - "copy", "paste", "cut"
        - "copy line", "cut line"
        - "copy word", "cut word"
        - "undo", "redo"
        
        #### Symbols
        - Quotes: "double quote", "single quote"
        - Brackets: "open bracket", "close bracket", "square bracket"
        - Punctuation: "comma", "period", "semicolon"
        - Math: "plus", "minus", "equals"
        - Special: "underscore", "at sign", "hash"
        """)

if __name__ == "__main__":
    main() 