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

def request_microphone_permission():
    """Request microphone permission using Streamlit's audio recorder"""
    st.info("⚠️ Microphone access is required for this application.")
    
    # Use Streamlit's audio recorder to trigger browser permission
    audio_permission = st.audio_recorder(
        text="Click here to enable microphone access",
        recording_color="#e8b62c",
        neutral_color="#6c757d"
    )
    
    if audio_permission is not None:
        st.session_state.microphone_permitted = True
        st.success("✅ Microphone access granted! You can now use voice commands.")
        st.rerun()
    elif 'microphone_permitted' not in st.session_state:
        st.warning("""
        👆 Please click the button above to enable microphone access.
        
        If you don't see a permission prompt:
        1. Check your browser settings
        2. Make sure microphone access isn't blocked
        3. Try using a different browser (Chrome recommended)
        """)

def check_environment():
    """Check the running environment and available features"""
    env_info = {
        'can_record_audio': False,
        'is_cloud': True,
        'error_message': None,
        'needs_permission': False
    }
    
    # Check if we're running in the cloud
    if os.path.exists('/mount/src'):
        try:
            # Try to import required packages first
            import speech_recognition as sr
            import pyaudio
            
            # If imports succeed, we might be able to use microphone with permission
            env_info['needs_permission'] = True
            env_info['error_message'] = None
            return env_info
            
        except ImportError as e:
            env_info['error_message'] = """
            ⚠️ Audio libraries not available in cloud environment.
            
            This application requires local installation to work properly because it needs:
            1. Microphone access
            2. System keyboard control
            
            To run locally:
            1. Clone the repository
            2. Install dependencies:
               ```
               pip install streamlit SpeechRecognition pyttsx3 PyAutoGUI
               
               # For Windows:
               # Download PyAudio wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
               # Then: pip install PyAudio-0.2.13-cp311-cp311-win_amd64.whl
               
               # For Linux:
               # sudo apt-get install python3-pyaudio
               
               # For Mac:
               # brew install portaudio
               # pip install pyaudio
               ```
            3. Run: streamlit run voice_keyboard.py
            """
            return env_info
    
    # Try to import required packages
    try:
        import speech_recognition as sr
        import pyttsx3
        import pyaudio
        env_info['can_record_audio'] = True
    except ImportError as e:
        if "pyaudio" in str(e).lower():
            env_info['error_message'] = """
            ⚠️ PyAudio is not installed. This is required for microphone access.
            
            Installation instructions:
            
            Windows:
            1. Download PyAudio wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
               - For Python 3.11: PyAudio-0.2.13-cp311-cp311-win_amd64.whl
            2. Install with: pip install PyAudio-0.2.13-cp311-cp311-win_amd64.whl
            
            Linux:
            - Run: sudo apt-get install python3-pyaudio
            
            Mac:
            1. Run: brew install portaudio
            2. Run: pip install pyaudio
            """
        else:
            env_info['error_message'] = f"Missing required package: {str(e)}"
        return env_info
    
    # Check for display access
    try:
        if sys.platform.startswith('win'):  # Windows
            import pyautogui
            env_info['is_cloud'] = False
        elif sys.platform.startswith('darwin'):  # macOS
            import pyautogui
            env_info['is_cloud'] = False
        elif sys.platform.startswith('linux'):  # Linux
            if os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY'):
                import pyautogui
                env_info['is_cloud'] = False
    except ImportError:
        env_info['error_message'] = "PyAutoGUI not available. Running in demo mode."
    except Exception as e:
        env_info['error_message'] = f"Display access error: {str(e)}"
    
    return env_info

# Initialize environment
if 'env_checked' not in st.session_state:
    env_info = check_environment()
    st.session_state.update(env_info)
    st.session_state.env_checked = True

class VoiceKeyboard:
    def __init__(self):
        self.is_cloud = st.session_state.is_cloud
        self.pyautogui = None
        
        # Initialize PyAutoGUI if not in cloud mode
        if not self.is_cloud:
            try:
                import pyautogui
                self.pyautogui = pyautogui
                self.pyautogui.FAILSAFE = False
            except Exception as e:
                st.error(f"Failed to initialize PyAutoGUI: {str(e)}")
                self.is_cloud = True
        
        if st.session_state.can_record_audio or (st.session_state.needs_permission and st.session_state.get('microphone_permitted', False)):
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            
            # Initialize text-to-speech only if not in cloud
            if not self.is_cloud:
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
        """Execute a keyboard command"""
        if self.is_cloud or not self.pyautogui:
            st.write(f"Demo Mode - Would execute: {command}")
            return
            
        try:
            if command == "copy":
                self.pyautogui.hotkey('ctrl', 'c')
            elif command == "paste":
                self.pyautogui.hotkey('ctrl', 'v')
            elif command == "select all":
                self.pyautogui.hotkey('ctrl', 'a')
            elif command == "undo":
                self.pyautogui.hotkey('ctrl', 'z')
            elif command == "redo":
                self.pyautogui.hotkey('ctrl', 'y')
            elif command == "save":
                self.pyautogui.hotkey('ctrl', 's')
            elif command == "cut":
                self.pyautogui.hotkey('ctrl', 'x')
            elif command == "new line":
                self.pyautogui.press('enter')
            elif command == "tab":
                self.pyautogui.press('tab')
            elif command == "space":
                self.pyautogui.press('space')
            elif command == "backspace":
                self.pyautogui.press('backspace')
            elif command == "delete":
                self.pyautogui.press('delete')
            elif command == "up":
                self.pyautogui.press('up')
            elif command == "down":
                self.pyautogui.press('down')
            elif command == "left":
                self.pyautogui.press('left')
            elif command == "right":
                self.pyautogui.press('right')
            elif command == "home":
                self.pyautogui.press('home')
            elif command == "end":
                self.pyautogui.press('end')
            elif command == "page up":
                self.pyautogui.press('pageup')
            elif command == "page down":
                self.pyautogui.press('pagedown')
            elif command == "escape":
                self.pyautogui.press('esc')
            else:
                # Type the command as text
                self.pyautogui.write(command)
        except Exception as e:
            st.error(f"Error executing command: {str(e)}")
            self.is_cloud = True
            self.pyautogui = None

    def type_symbol(self, symbol_name):
        """Handle typing of symbols"""
        if self.is_cloud:
            symbol = self.symbols.get(symbol_name, '')
            st.write(f"Symbol command received: {symbol_name} ({symbol})")
            return True
            
        if symbol_name in self.symbols:
            try:
                symbol = self.symbols[symbol_name]
                if len(symbol) == 2:  # For paired symbols like (), [], {}
                    self.pyautogui.write(symbol[0])
                    self.pyautogui.write(symbol[1])
                    self.pyautogui.press('left')
                else:
                    self.pyautogui.write(symbol)
                return True
            except Exception as e:
                st.error(f"Error typing symbol: {str(e)}")
                self.is_cloud = True  # Switch to cloud mode if symbol typing fails
        return False

    def speak(self, text):
        """Text to speech feedback"""
        if not self.is_cloud and self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                st.warning(f"Text-to-speech failed: {str(e)}")

    def process_command(self, text):
        """Process voice command and execute appropriate action"""
        text = text.lower().strip()
        
        # Check for stop commands
        if text in ["stop listening", "stop now", "finish"]:
            return True
            
        # Navigation commands
        if text in ["go left", "go right", "word left", "word right"]:
            direction = text.split()[-1]
            if not self.is_cloud and self.pyautogui:
                self.pyautogui.press(direction)
            else:
                st.write(f"Demo Mode - Would navigate: {direction}")
            return False
            
        # Special commands
        if text.startswith("type "):
            text = text[5:]  # Remove "type " prefix
        
        # Execute the command
        self.execute_command(text)
        return False

    def listen(self):
        """Listen for voice input"""
        if not (st.session_state.can_record_audio or (st.session_state.needs_permission and st.session_state.get('microphone_permitted', False))):
            st.error("Audio recording is not available")
            return ""
            
        try:
            with sr.Microphone() as source:
                # Reduced duration for faster startup
                self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
                try:
                    # Reduced timeout and added phrase_time_limit for faster response
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=2)
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
            st.error(f"Error accessing microphone: {str(e)}")
            if 'microphone_permitted' in st.session_state:
                del st.session_state.microphone_permitted
            return ""

def main():
    st.title("Voice Keyboard Assistant 🎤")
    
    # Check if we need to request microphone permission
    if st.session_state.needs_permission and not st.session_state.get('microphone_permitted', False):
        request_microphone_permission()
        return
    
    # Display any error messages first
    if st.session_state.error_message:
        st.error(st.session_state.error_message)
        return
    
    # Create tabs for different sections
    main_tab, info_tab = st.tabs(["Main", "System Information"])
    
    with main_tab:
        # Display environment information
        if st.session_state.is_cloud and not st.session_state.get('microphone_permitted', False):
            st.warning("""
            ⚠️ **Cloud/Demo Mode Active**
            
            This application requires:
            1. Microphone access
            2. Local system access for keyboard control
            
            Please run this application locally:
            1. Clone the repository
            2. Install dependencies from requirements.txt
            3. Run `streamlit run voice_keyboard.py`
            """)
            return
        
        st.success("✅ Running in full functionality mode with keyboard control enabled.")
        
        voice_keyboard = VoiceKeyboard()
        
        # Create a test textarea
        test_text = st.text_area("Test your voice commands here:", height=200)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Start Listening", type="primary", 
                        disabled=not (st.session_state.can_record_audio or 
                                    (st.session_state.needs_permission and 
                                     st.session_state.get('microphone_permitted', False)))):
                if not (st.session_state.can_record_audio or 
                       (st.session_state.needs_permission and 
                        st.session_state.get('microphone_permitted', False))):
                    st.error("Cannot start listening - audio recording is not available")
                    return
                    
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
        st.write(f"Audio Available: {st.session_state.can_record_audio or (st.session_state.needs_permission and st.session_state.get('microphone_permitted', False))}")
        st.write(f"Mode: {'Cloud/Demo' if st.session_state.is_cloud else 'Full Functionality'}")
        
        if st.session_state.error_message:
            st.write("### Error Details")
            st.error(st.session_state.error_message)
        
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