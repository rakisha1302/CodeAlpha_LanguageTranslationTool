# 🌐 GlobeTalk – AI-Powered Smart Language Translation Assistant

Streamlit app: translation with auto-detect, voice-to-text (Groq Whisper), text-to-speech (gTTS),
grammar correction, tone conversion, context-aware translation, travel phrasebook, AI conversation
practice, and SQLite history with search/export.

## Run locally
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # add your Groq key
streamlit run app.py
```
Get a free key at https://console.groq.com. Without a key, plain translation, detection, phrasebook
and TTS still work; AI features show a friendly prompt.

## Deploy on Streamlit Cloud
1. Push this folder to GitHub (`secrets.toml` and `*.db` are git-ignored).
2. https://share.streamlit.io → New app → select repo, main file `app.py`.
3. App settings → Secrets → paste `GROQ_API_KEY = "gsk_..."`.

Note: the SQLite file on Streamlit Cloud resets when the app restarts (ephemeral disk).

## Structure
```
app.py                UI (dashboard + pages)
modules/config.py     languages, secure key lookup
modules/translator.py translation + detection
modules/ai.py         Groq: grammar, tone, context, practice, STT
modules/speech.py     text-to-speech
modules/db.py         SQLite history
modules/phrasebook.py travel phrases
tests/test_core.py    pytest suite
```
Run tests: `pytest -q`
