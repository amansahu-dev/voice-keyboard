import streamlit as st
import platform
import sys
import os
import time
import speech_recognition as sr
import pyttsx3
import pyautogui

# Configure the application
st.set_page_config(
    page_title="Voice Keyboard Assistant",
    page_icon="🎤",
    layout="wide"
)

class VoiceKeyboard:
    def __init__(self):
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 0.8
        self.recognizer.non_speaking_duration = 0.5
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        
        # Initialize text-to-speech
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
        except Exception:
            self.engine = None
        
        # Configure PyAutoGUI
        pyautogui.FAILSAFE = False

        # Define special commands
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
            
            # Word deletion commands
            'remove word': [['shift', 'ctrl', 'left'], ['delete']],
            'delete word': [['shift', 'ctrl', 'left'], ['delete']],
            'remove last word': [['shift', 'ctrl', 'left'], ['delete']],
            'back word': [['shift', 'ctrl', 'left'], ['delete']],
            
            # Undo/Redo
            'undo': ['ctrl', 'z'],
            'redo': ['ctrl', 'y'],
            
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
        
        # Define symbols
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
        except Exception as e:
            st.error(f"Error executing command: {str(e)}")

    def type_symbol(self, symbol_name):
        """Handle typing of symbols"""
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
        return False

    def process_command(self, text):
        """Process voice command and execute appropriate action"""
        if not text:
            return False

        text = text.lower().strip()
        
        # Check for stop commands
        if text in ["stop listening", "stop now", "finish", "stop recording", "end recording"]:
            return True
            
        # Split into words
        words = text.split()
        i = 0
        while i < len(words):
            # Try three-word commands
            if i + 2 < len(words):
                three_word_cmd = f"{words[i]} {words[i+1]} {words[i+2]}"
                if three_word_cmd in self.special_commands:
                    self.execute_command(self.special_commands[three_word_cmd])
                    i += 3
                    continue

            # Try two-word commands
            if i + 1 < len(words):
                two_word_cmd = f"{words[i]} {words[i+1]}"
                if two_word_cmd in self.special_commands:
                    self.execute_command(self.special_commands[two_word_cmd])
                    i += 2
                    continue
                # Check for symbols
                if self.type_symbol(two_word_cmd):
                    i += 2
                    continue

            # Try single-word commands
            if words[i] in self.special_commands:
                self.execute_command(self.special_commands[words[i]])
                i += 1
                continue
            
            # Check for single-word symbols
            if self.type_symbol(words[i]):
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
        try:
            with sr.Microphone() as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
                try:
                    # Listen for input
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=2)
                    text = self.recognizer.recognize_google(audio)
                    return text
                except sr.WaitTimeoutError:
                    return ""
                except sr.UnknownValueError:
                    return ""
                except sr.RequestError:
                    st.error("Could not connect to speech recognition service")
                    return ""
        except Exception as e:
            st.error(f"Error accessing microphone: {str(e)}")
            return ""

def main():
    st.title("Voice Keyboard Assistant 🎤")
    
    # Create tabs
    main_tab, help_tab = st.tabs(["Main", "Help"])
    
    with main_tab:
        st.success("✅ Voice Keyboard Assistant is ready!")
        
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
    
    with help_tab:
        st.write("### Available Commands")
        
        st.write("#### Basic Navigation")
        st.write("""
        - "enter", "next line", "new line", "press enter"
        - "space", "tab"
        - "backspace", "delete"
        - "escape"
        """)
        
        st.write("#### Word Operations")
        st.write("""
        - "remove word", "delete word", "back word"
        - "capital [word]" (capitalizes next word)
        - "all caps" (toggles caps lock)
        """)
        
        st.write("#### Navigation Commands")
        st.write("""
        - "go left", "go right", "go up", "go down"
        - "word left", "word right"
        - "go to start", "go to end"
        - "line start", "line end"
        - "first line", "last line"
        - "page up", "page down"
        """)
        
        st.write("#### Selection Commands")
        st.write("""
        - "select word", "select line"
        - "select next word", "select previous word"
        - "select up", "select down"
        - "select to start", "select to end"
        - "select all"
        """)
        
        st.write("#### Copy/Paste Commands")
        st.write("""
        - "copy", "paste", "cut"
        - "copy line", "cut line"
        - "copy word", "cut word"
        - "undo", "redo"
        """)
        
        st.write("#### Symbols")
        st.write("""
        Quotes:
        - "double quote", "single quote", "quotes", "quote"
        
        Brackets:
        - "open bracket", "close bracket"
        - "round bracket", "parenthesis"
        - "square bracket"
        - "curly bracket", "curly braces"
        
        Common Symbols:
        - "comma", "period", "dot"
        - "semicolon", "colon"
        - "dash", "hyphen"
        - "underscore"
        - "equals", "plus", "minus"
        - "asterisk", "star"
        - "forward slash", "backslash"
        - "pipe"
        - "at sign", "hash"
        - "dollar", "percent"
        - "caret", "ampersand"
        - "exclamation", "question mark"
        - "greater than", "less than"
        - "tilde"
        """)
        
        st.write("#### Control Commands")
        st.write("""
        - "stop listening", "stop now", "finish"
        - "stop recording", "end recording"
        """)
        
        st.write("### Tips")
        st.write("""
        1. Speak clearly and at a moderate pace
        2. Use natural phrases - most commands are intuitive
        3. For typing text, just speak normally
        4. Use "capital" before a word to capitalize it
        5. Commands can be combined in natural ways
        """)

if __name__ == "__main__":
    main() 