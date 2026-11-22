
"""Configuration and secure API-key lookup (secrets -> env -> session)."""

import os
import streamlit as st

# Groq AI models
MODEL = "openai/gpt-oss-120b"
STT_MODEL = "whisper-large-v3-turbo"

# Database
DB_PATH = os.getenv(
    "GLOBETALK_DB",
    os.path.join("data", "globetalk.db")
)

# Supported languages
LANGS = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Hindi": "hi",
    "Tamil": "ta",
    "Telugu": "te",
    "Malayalam": "ml",
    "Bengali": "bn",
    "Arabic": "ar",
    "Russian": "ru",
    "Japanese": "ja",
    "Korean": "ko",
    "Chinese (Simplified)": "zh-CN",
    "Turkish": "tr",
    "Dutch": "nl",
    "Thai": "th",
    "Indonesian": "id",
}

CODE_TO_NAME = {
    code.lower(): name
    for name, code in LANGS.items()
}

TONES = ["Formal", "Friendly", "Casual"]


def lang_name(code: str) -> str:
    """Convert language code into its display name."""
    return CODE_TO_NAME.get(
        (code or "").lower(),
        code
    )


def get_groq_key():
    """Get API key from secrets, environment, or session."""

    # 1. Streamlit secrets
    try:
        key = st.secrets.get("GROQ_API_KEY")
        if key:
            return key.strip()
    except Exception:
        pass

    # 2. Environment variable (.env)
    key = os.getenv("GROQ_API_KEY")
    if key:
        return key.strip()

    # 3. Sidebar session input
    try:
        key = st.session_state.get("user_key")
        if key:
            return key.strip()
    except Exception:
        pass

    return None
