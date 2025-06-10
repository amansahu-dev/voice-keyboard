import speech_recognition as sr
import streamlit as st
import pyttsx3
import time
import re
import platform
import sys
import os

# Must be the first Streamlit command
st.set_page_config(page_title="Voice Keyboard Assistant", page_icon="🎤")

# Check if running in cloud or if display is available
IS_CLOUD = True  # Default to cloud/no-display mode
try:
    # Only try to import pyautogui if we're in a suitable environment
    if sys.platform.startswith('win'):  # Windows
        import pyautogui
        IS_CLOUD = False
    elif sys.platform.startswith('darwin'):  # macOS
        import pyautogui
        IS_CLOUD = False
    elif sys.platform.startswith('linux'):  # Linux
        # Check if running in a desktop environment
        if os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY'):
            import pyautogui
            IS_CLOUD = False
        else:
            st.info("No display available. Running in cloud/demo mode.")
    else:
        st.info("Unsupported platform. Running in cloud/demo mode.")
except ImportError:
    st.info("PyAutoGUI not available. Running in cloud/demo mode.")
except Exception as e:
    st.info(f"Display access error. Running in cloud/demo mode. Error: {str(e)}")

# Initialize PyAutoGUI if available
if not IS_CLOUD:
    try:
        pyautogui.FAILSAFE = False
    except Exception:
        IS_CLOUD = True
        st.info("Failed to initialize PyAutoGUI. Running in cloud/demo mode.")

class VoiceKeyboard:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
        # Initialize text-to-speech only if not in cloud
        if not IS_CLOUD:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', 150)
            except Exception as e:
                st.info(f"Text-to-speech initialization failed: {str(e)}")
                self.engine = None
        else:
            self.engine = None
        
        # Fix speech recognition settings
        self.recognizer.pause_threshold = 0.8
        self.recognizer.non_speaking_duration = 0.5
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.operation_timeout = None
        
        # Define commands with their variations
        self.special_commands = {
            # Basic navigation
            'enter': 'enter',
            'space': 'space',
            'tab': 'tab',
            'backspace': 'backspace',
            'delete': 'delete',
            'escape': 'escape',
            'next line': 'enter',
            'new line': 'enter',
            'press enter': 'enter',
            
            # Word deletion commands - Fixed implementation
            'remove word': [['shift', 'ctrl', 'left'], ['delete']],
            'delete word': [['shift', 'ctrl', 'left'], ['delete']],
            'remove last word': [['shift', 'ctrl', 'left'], ['delete']],
            'back word': [['shift', 'ctrl', 'left'], ['delete']],
            
            # Undo/Redo
            'undo': ['ctrl', 'z'],
            'redo': ['ctrl', 'y'],
            
            # Stop commands
            'stop listening': 'stop',
            'stop recording': 'stop',
            'stop now': 'stop',
            'finish': 'stop',
            'end recording': 'stop',
            
            # Case commands
            'capital': 'capslock',
            'caps lock': 'capslock',
            'shift': 'shift',
            'all caps': ['capslock', 'capslock'],
            
            # Navigation commands
            'go left': 'left',
            'go right': 'right',
            'go up': 'up',
            'go down': 'down',
            'word left': ['ctrl', 'left'],
            'word right': ['ctrl', 'right'],
            'go to start': ['ctrl', 'home'],
            'go to end': ['ctrl', 'end'],
            'go to beginning': ['ctrl', 'home'],
            'line start': 'home',
            'line end': 'end',
            'first line': ['ctrl', 'home'],
            'last line': ['ctrl', 'end'],
            'page up': 'pageup',
            'page down': 'pagedown',
            
            # Copy and Paste Commands
            'copy': ['ctrl', 'c'],
            'paste': ['ctrl', 'v'],
            'cut': ['ctrl', 'x'],
            'select all': ['ctrl', 'a'],
            
            # Selection Commands
            'select word': ['ctrl', 'shift', 'right'],
            'select line': [['end'], ['shift', 'home']],
            'select next word': ['shift', 'ctrl', 'right'],
            'select previous word': ['shift', 'ctrl', 'left'],
            
            # Copy specific content
            'copy line': [['end'], ['shift', 'home'], ['ctrl', 'c']],
            'copy word': [['ctrl', 'shift', 'right'], ['ctrl', 'c']],
            'cut line': [['end'], ['shift', 'home'], ['ctrl', 'x']],
            'cut word': [['ctrl', 'shift', 'right'], ['ctrl', 'x']],
            
            # Select multiple lines
            'select up': ['shift', 'up'],
            'select down': ['shift', 'down'],
            'select to start': ['shift', 'home'],
            'select to end': ['shift', 'end'],
        }
        
        self.symbols = {
            # Quotes
            'double quote': '"',
            'single quote': "'",
            'quotes': '"',
            'quote': "'",
            
            # Brackets
            'open bracket': '(',
            'close bracket': ')',
            'round bracket': '()',
            'parenthesis': '()',
            'square bracket': '[]',
            'curly bracket': '{}',
            'curly braces': '{}',
            
            # Common symbols
            'comma': ',',
            'period': '.',
            'dot': '.',
            'semicolon': ';',
            'colon': ':',
            'dash': '-',
            'hyphen': '-',
            'underscore': '_',
            'equals': '=',
            'plus': '+',
            'minus': '-',
            'asterisk': '*',
            'star': '*',
            'forward slash': '/',
            'backslash': '\\',
            'pipe': '|',
            'at sign': '@',
            'hash': '#',
            'dollar': '$',
            'percent': '%',
            'caret': '^',
            'ampersand': '&',
            'exclamation': '!',
            'question mark': '?',
            'greater than': '>',
            'less than': '<',
            'tilde': '~'
        }

    def execute_command(self, command):
        """Execute a command with proper timing"""
        if IS_CLOUD:
            # In cloud environment, just display the command
            if isinstance(command, list):
                if isinstance(command[0], list):
                    st.write(f"Command sequence received: {command}")
                else:
                    st.write(f"Hotkey command received: {'+'.join(command)}")
            else:
                st.write(f"Key command received: {command}")
            return False
            
        if command == 'stop':
            return True
        
        try:
            if isinstance(command, list):
                # Handle nested commands (for complex operations)
                if isinstance(command[0], list):
                    for cmd in command:
                        pyautogui.hotkey(*cmd)
                        time.sleep(0.1)
                else:
                    pyautogui.hotkey(*command)
            else:
                pyautogui.press(command)
            
            time.sleep(0.05)
        except Exception as e:
            st.error(f"Error executing command: {str(e)}")
            IS_CLOUD = True  # Switch to cloud mode if command execution fails
        
        return False

    def type_symbol(self, symbol_name):
        """Handle typing of symbols"""
        if IS_CLOUD:
            symbol = self.symbols.get(symbol_name, '')
            st.write(f"Symbol command received: {symbol_name} ({symbol})")
            return True
            
        if symbol_name in self.symbols:
            try:
                symbol = self.symbols[symbol_name]
                if len(symbol) == 2:  # For paired symbols like (), [], {}
                    pyautogui.write(symbol[0])
                    pyautogui.write(symbol[1])
                    pyautogui.press('left')
                else:
                    pyautogui.write(symbol)
                return True
            except Exception as e:
                st.error(f"Error typing symbol: {str(e)}")
                IS_CLOUD = True  # Switch to cloud mode if symbol typing fails
        return False

    def speak(self, text):
        """Text to speech feedback"""
        if not IS_CLOUD and self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                st.warning(f"Text-to-speech failed: {str(e)}")

    def process_command(self, text):
        """Process the voice command and perform actions"""
        if not text:
            return False

        # Convert to lowercase and get words
        text = text.lower().strip()
        words = text.split()

        # Check for stop commands first
        stop_commands = ['stop listening', 'stop recording', 'stop now', 'finish', 'end recording']
        if text in stop_commands:
            return True

        # Try to match the longest possible command first
        i = 0
        while i < len(words):
            # Try three-word commands
            if i + 2 < len(words):
                three_word_cmd = f"{words[i]} {words[i+1]} {words[i+2]}"
                if three_word_cmd in self.special_commands:
                    command = self.special_commands[three_word_cmd]
                    self.execute_command(command)
                    i += 3
                    continue

            # Try two-word commands
            if i + 1 < len(words):
                two_word_cmd = f"{words[i]} {words[i+1]}"
                if two_word_cmd in self.special_commands:
                    command = self.special_commands[two_word_cmd]
                    self.execute_command(command)
                    i += 2
                    continue

            # Try single-word commands
            if words[i] in self.special_commands:
                command = self.special_commands[words[i]]
                self.execute_command(command)
                i += 1
                continue

            # Check for capitalization
            if words[i] == "capital" and i + 1 < len(words):
                pyautogui.write(words[i + 1].capitalize())
                i += 2
                continue

            # If no command matched, type the word
            pyautogui.write(words[i] + " ")
            i += 1

        return False

    def listen(self):
        """Listen for voice input"""
        with sr.Microphone() as source:
            try:
                # Safely adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                
                # Listen for input with appropriate timeouts
                audio = self.recognizer.listen(source, 
                                             timeout=3,  # Wait up to 3 seconds for phrase to start
                                             phrase_time_limit=5)  # Listen up to 5 seconds
                
                text = self.recognizer.recognize_google(audio)
                return text
            except sr.WaitTimeoutError:
                return ""
            except sr.UnknownValueError:
                return ""
            except sr.RequestError:
                st.error("Could not connect to the speech recognition service")
                return ""
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                return ""

def main():
    st.title("Voice Keyboard Assistant 🎤")
    
    # Create tabs for different sections
    main_tab, info_tab = st.tabs(["Main", "System Information"])
    
    with main_tab:
        # Display environment information
        if IS_CLOUD:
            st.warning("""
            ⚠️ **Cloud/Demo Mode Active**
            
            This application is running in a limited environment where keyboard control features are not available.
            The application will demonstrate voice recognition and show what actions would be taken.
            
            For full functionality including keyboard control:
            1. Download and run the application locally
            2. Make sure you have a display/desktop environment
            3. Run `streamlit run voice_keyboard.py`
            
            Current features available:
            - Voice recognition
            - Command detection
            - Command visualization
            """)
        else:
            st.success("✅ Running in full functionality mode with keyboard control enabled.")
        
        voice_keyboard = VoiceKeyboard()
        
        # Create a test textarea
        test_text = st.text_area("Test your voice commands here:", height=200)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Start Listening", type="primary"):
                st.session_state.listening = True
                st.success("Listening... Speak now!")
                
                while st.session_state.get('listening', False):
                    text = voice_keyboard.listen()
                    if text:
                        st.write(f"Recognized: {text}")
                        should_stop = voice_keyboard.process_command(text)
                        if should_stop:
                            st.session_state.listening = False
                            st.info("Stopped listening")
                            break
                    time.sleep(0.05)
        
        with col2:
            if st.button("Stop", type="secondary"):
                st.session_state.listening = False
                st.info("Stopped listening")
    
    with info_tab:
        # Display system information
        st.write("### System Information")
        st.write(f"Platform: {platform.platform()}")
        st.write(f"Python Version: {platform.python_version()}")
        st.write(f"Display Available: {bool(os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY'))}")
        st.write(f"Mode: {'Cloud/Demo' if IS_CLOUD else 'Full Functionality'}")
        
        # Display available commands
        st.write("### Available Commands")
        st.write("""
        - Regular text: Just speak normally
        - Stop Commands: "Stop listening", "Stop now", "Finish"
        - Delete: "Remove word", "Delete word", "Back word"
        - Navigation: "Go left", "Go right", "Word left", "Word right"
        - Advanced Navigation: "Go to start", "Go to end", "Line start", "Line end"
        - Copy/Paste: "Copy line", "Copy word", "Paste", "Cut line"
        - Selection: "Select word", "Select line", "Select up", "Select down"
        - Symbols: "Double quote", "Open bracket", "Comma", etc.
        """)

if __name__ == "__main__":
    main() 