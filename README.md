# Voice Keyboard Assistant

A Python-based voice-controlled keyboard assistant that allows you to type and control your keyboard using voice commands.

## Features

- Voice-to-text input
- Special key commands (Enter, Space, Tab, etc.)
- Capitalization control
- Real-time voice recognition
- User-friendly Streamlit interface
- Text-to-speech feedback

## Local Development Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd python-voice-tool
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application locally:
```bash
streamlit run voice_keyboard.py
```

## Deployment

### Deploy to Streamlit Cloud

1. Push your code to GitHub:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Sign in with your GitHub account
4. Click "New app"
5. Select your repository and branch
6. Set the main file path as: `voice_keyboard.py`
7. Click "Deploy"

### Updating the Deployed Application

1. Make changes to your code locally
2. Test the changes:
```bash
streamlit run voice_keyboard.py
```

3. Commit and push changes:
```bash
git add .
git commit -m "Description of changes"
git push
```

4. Streamlit Cloud will automatically detect the changes and redeploy your app

## Important Notes

1. **Automatic Updates**: Streamlit Cloud automatically redeploys your app when you push changes to the connected GitHub repository.

2. **Environment Variables**: If you add any environment variables or secrets:
   - Add them to Streamlit Cloud's deployment settings
   - Never commit sensitive information to Git

3. **Dependencies**: If you update `requirements.txt`:
   - The changes will be automatically detected
   - New dependencies will be installed during redeployment

4. **Browser Permissions**: Users will need to grant microphone permissions when using the deployed app

## Troubleshooting

1. If PyAudio installation fails:
   - Windows: `pip install pipwin` followed by `pipwin install pyaudio`
   - Linux: `sudo apt-get install python3-pyaudio`
   - Mac: `brew install portaudio` followed by `pip install pyaudio`

2. If the app doesn't update after pushing changes:
   - Check the deployment logs in Streamlit Cloud
   - Ensure all dependencies are in `requirements.txt`
   - Try forcing a manual redeployment in Streamlit Cloud

## Version Control Best Practices

1. Always create a new branch for features:
```bash
git checkout -b feature/new-feature
```

2. Test changes locally before pushing:
```bash
streamlit run voice_keyboard.py
```

3. Create meaningful commit messages:
```bash
git commit -m "Add: new voice command for [feature]"
```

4. Merge changes through pull requests for better tracking

## Prerequisites

- Python 3.7 or higher
- A working microphone
- Internet connection (for Google Speech Recognition)

## Usage

1. Run the application:
```bash
streamlit run voice_keyboard.py
```

2. Click the "Start Listening" button to begin voice recognition
3. Speak your commands clearly
4. Click "Stop" when you're done

## Voice Commands

- Regular text: Just speak normally
- Capitalization: Say "Capital [word]"
- New line: Say "Press enter" or "next line"
- Special keys: Say "Press [key]" where key can be:
  - enter
  - space
  - tab
  - backspace
  - delete
  - escape

## Examples

- "My name is John press enter"
- "Capital Hello world"
- "Press tab"
- "This is a new sentence press enter"

## Note

The application uses Google Speech Recognition API, so an internet connection is required for voice recognition to work. 