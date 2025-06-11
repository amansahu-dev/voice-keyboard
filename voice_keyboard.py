import streamlit as st
import speech_recognition as sr
import pyttsx3
import pyautogui
import time

# Configure the application
st.set_page_config(
    page_title="Voice Keyboard Assistant",
    page_icon="🎤",
    layout="wide"
)

# Add beautiful styling
st.markdown("""
<style>
    .stButton > button {
        font-size: 20px;
        padding: 15px 30px;
        border-radius: 50px;
        border: none;
        background: linear-gradient(45deg, #ff4b4b, #ff6b6b);
        color: white;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.2);
        transition: all 0.3s ease;
        font-weight: 500;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 75, 75, 0.3);
        background: linear-gradient(45deg, #ff6b6b, #ff4b4b);
    }
    .stButton > button:active {
        transform: translateY(0px);
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.2);
    }
    .status-text {
        text-align: center;
        padding: 10px;
        border-radius: 10px;
        margin: 10px 0;
        font-weight: 500;
    }
    .listening {
        background: linear-gradient(45deg, rgba(255, 75, 75, 0.1), rgba(255, 107, 107, 0.1));
        color: #ff4b4b;
    }
    .stopped {
        background: rgba(128, 128, 128, 0.1);
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# Initialize the recognizer
r = sr.Recognizer()
r.pause_threshold = 0.5
r.energy_threshold = 300

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
    'stop listening': 'stop',  # Special command to stop listening
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
    'copy line': ['ctrl', 'l', 'ctrl', 'c'],
    'cut line': ['ctrl', 'l', 'ctrl', 'x'],
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

def update_status(message, message_type="info"):
    """Update the status message with appropriate styling"""
    if message_type == "error":
        st.session_state.message_placeholder.error(message)
    elif message_type == "success":
        st.session_state.message_placeholder.success(message)
    elif message_type == "warning":
        st.session_state.message_placeholder.warning(message)
    else:
        st.session_state.message_placeholder.info(message)

def process_command(command):
    """Process voice commands and execute corresponding actions"""
    command = command.lower().strip()
    result = ""
    
    # Check for stop command first
    if command in ['stop', 'stop listening', 'quit', 'exit']:
        st.session_state.is_listening = False
        st.rerun()  # Force a rerun to update the UI
        return "Stopping voice assistant..."
    
    # Process the entire command at once
    if command in SPECIAL_KEYS:
        if SPECIAL_KEYS[command] == 'stop':
            st.session_state.is_listening = False
            st.rerun()  # Force a rerun to update the UI
            return "Stopping voice assistant..."
        pyautogui.press(SPECIAL_KEYS[command])
        result = f"Executed: {command}"
    elif command in NAVIGATION_KEYS:
        keys = NAVIGATION_KEYS[command]
        if isinstance(keys, list):
            pyautogui.hotkey(*keys)
        else:
            pyautogui.press(keys)
        result = f"Executed: {command}"
    elif command in SELECTION_KEYS:
        pyautogui.hotkey(*SELECTION_KEYS[command])
        result = f"Selected: {command}"
    elif command in EDIT_KEYS:
        pyautogui.hotkey(*EDIT_KEYS[command])
        result = f"Executed: {command}"
    elif command in SYMBOLS:
        pyautogui.write(SYMBOLS[command])
        result = f"Typed symbol: {command}"
    else:
        pyautogui.write(command + " ")
        result = f"Typed: {command}"
    
    return result

def listen_continuously():
    """Listen for voice commands continuously"""
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            update_status("🎤 Listening... Speak your command")
            
            while st.session_state.is_listening:
                try:
                    audio = r.listen(source, timeout=1, phrase_time_limit=5)
                    text = r.recognize_google(audio).lower()
                    
                    if text:
                        st.session_state.current_query = text
                        update_status(f"Recognized: {text}", "info")
                        result = process_command(text)
                        if result == "Stopping voice assistant...":
                            st.session_state.is_listening = False
                            update_status("Voice assistant stopped!", "warning")
                            break
                        update_status(result, "success")
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    update_status("Could not understand audio", "error")
                    continue
                except sr.RequestError:
                    update_status("Could not connect to speech recognition service", "error")
                    st.session_state.is_listening = False
                    break
                except Exception as e:
                    update_status(f"Error: {str(e)}", "error")
                    st.session_state.is_listening = False
                    break
                
                time.sleep(0.1)
                
    except Exception as e:
        update_status(f"Microphone Error: {str(e)}", "error")
        st.session_state.is_listening = False

def main():
    st.title("Voice Keyboard Assistant 🎤")
    
    # Initialize session state
    if 'is_listening' not in st.session_state:
        st.session_state.is_listening = False
    if 'current_query' not in st.session_state:
        st.session_state.current_query = ""
        
    def toggle_listening():
        st.session_state.is_listening = not st.session_state.is_listening
    
    # Create tabs
    tab1, tab2 = st.tabs(["Main", "Help"])
    
    with tab1:
        # Add test textbox
        st.text_area("Test your voice commands here:", height=200, key="test_area")
        
        st.markdown("---")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Center align the content
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            
            # Toggle button with dynamic text
            button_text = "🎤 Stop Listening" if st.session_state.is_listening else "🎤 Start Listening"
            if st.button(button_text, key="toggle_button", on_click=toggle_listening):
                pass  # The toggle is handled in the on_click function
            
            # Show status with enhanced styling
            status_class = "listening" if st.session_state.is_listening else "stopped"
            status_text = "🔴 Listening..." if st.session_state.is_listening else "⚪ Click to Start"
            st.markdown(f"<div class='status-text {status_class}'>{status_text}</div>", unsafe_allow_html=True)
            
            if st.session_state.is_listening:
                if 'message_placeholder' not in st.session_state:
                    st.session_state.message_placeholder = st.empty()
                update_status("Starting voice assistant... Say commands clearly!")
                listen_continuously()
            
            st.markdown("</div>", unsafe_allow_html=True)
        
            # Create a single placeholder for all messages
            if 'message_placeholder' not in st.session_state:
                st.session_state.message_placeholder = st.empty()
                update_status("Click the button to begin")
        
        with col2:
            st.markdown("""
            ### Quick Tips
            1. Speak clearly and naturally
            2. Use commands like "capital [word]" for capitalization
            3. Say "enter" or "next line" for new lines
            4. Use navigation commands like "go left", "go right"
            5. Try selection commands like "select word", "select line"
            6. Say "stop listening" or click the button to stop
            """)

    with tab2:
        st.markdown("""
        ### Available Commands
        
        #### Basic Navigation
        - "enter", "next line", "new line"
        - "space", "tab"
        - "backspace", "delete"
        - "escape"
        - "stop listening", "stop" (stops the assistant)
        
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