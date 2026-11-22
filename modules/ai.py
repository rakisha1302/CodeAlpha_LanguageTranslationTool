
"""
GlobeTalk - Groq-powered AI features.

Features:
1. Grammar correction
2. Tone conversion
3. Context-aware translation
4. Custom travel phrases
5. AI conversation practice
6. Speech-to-text with automatic language detection
"""

import json

from groq import Groq
from .config import get_groq_key, MODEL, STT_MODEL


# --------------------------------------------------
# CUSTOM EXCEPTION
# --------------------------------------------------

class AIError(Exception):
    """Raised when an AI operation fails."""
    pass


# --------------------------------------------------
# GROQ CLIENT
# --------------------------------------------------

def _client():
    """Create a Groq client using the configured API key."""

    key = get_groq_key()

    if not key:
        raise AIError(
            "Groq API key missing. "
            "Add GROQ_API_KEY to your environment or Streamlit secrets."
        )

    try:
        return Groq(api_key=key)

    except Exception as e:
        raise AIError(f"Unable to connect to Groq: {e}")


# --------------------------------------------------
# COMMON AI CHAT FUNCTION
# --------------------------------------------------

def _chat(
    system,
    user=None,
    messages=None,
    json_mode=False,
    temperature=0.3
):
    """Send a request to Groq chat completion."""

    msgs = [
        {
            "role": "system",
            "content": system
        }
    ]

    if messages:
        msgs.extend(messages)

    else:
        msgs.append({
            "role": "user",
            "content": user
        })

    kwargs = {}

    if json_mode:
        kwargs["response_format"] = {
            "type": "json_object"
        }

    try:

        response = _client().chat.completions.create(
            model=MODEL,
            messages=msgs,
            temperature=temperature,
            **kwargs
        )

        output = (
            response.choices[0].message.content or ""
        ).strip()

        if not output:
            raise AIError("The AI returned an empty response.")

        if json_mode:

            try:
                return json.loads(output)

            except json.JSONDecodeError:
                raise AIError(
                    "The AI returned an unreadable answer. Please try again."
                )

        return output

    except AIError:
        raise

    except Exception as e:
        raise AIError(f"AI request failed: {e}")


# --------------------------------------------------
# GRAMMAR CORRECTION
# --------------------------------------------------

def correct_grammar(text, language):

    if not text.strip():
        raise AIError("Please enter text for grammar correction.")

    system = (
        f"You are a professional {language} grammar editor. "
        "Correct spelling, grammar and punctuation. "
        "Preserve the original meaning and language. "
        'Reply ONLY as JSON: '
        '{"corrected": str, "changes": [str], "explanation": str}.'
    )

    return _chat(
        system,
        text,
        json_mode=True,
        temperature=0.1
    )


# --------------------------------------------------
# TONE CONVERSION
# --------------------------------------------------

def convert_tone(text, tone, language):

    if not text.strip():
        raise AIError("Please enter text for tone conversion.")

    system = (
        f"Rewrite the user's text in {language} "
        f"with a {tone.lower()} tone. "
        "Preserve the original meaning. "
        "Return only the rewritten text."
    )

    return _chat(
        system,
        text,
        temperature=0.5
    )


# --------------------------------------------------
# CONTEXT-AWARE TRANSLATION
# --------------------------------------------------

def context_translate(text, src, tgt, context):

    if not text.strip():
        raise AIError("Please enter text to translate.")

    system = (
        f"Translate the text from {src} to {tgt}. "
        f"Context: {context}. "
        "Choose suitable words, idioms and expressions "
        "for this situation. "
        'Reply ONLY as JSON: '
        '{"translation": str, "notes": str}.'
    )

    return _chat(
        system,
        text,
        json_mode=True,
        temperature=0.3
    )


# --------------------------------------------------
# CUSTOM TRAVEL PHRASES
# --------------------------------------------------

def custom_phrases(scenario, tgt, n=6):

    if not scenario.strip():
        raise AIError("Please describe a travel situation.")

    system = (
        f"Create {n} useful traveller phrases in English "
        f"for this situation: {scenario}. "
        f"Translate each phrase into {tgt}. "
        'Reply ONLY as JSON: '
        '{"phrases": ['
        '{"english": str, '
        '"translation": str, '
        '"pronunciation": str}'
        ']}'
    )

    return _chat(
        system,
        scenario,
        json_mode=True,
        temperature=0.5
    )


# --------------------------------------------------
# AI CONVERSATION PRACTICE
# --------------------------------------------------

def practice_turn(history, language, level, scenario):

    system = (
        f"You are a friendly {language} conversation partner. "
        f"The learner's level is {level}. "
        f"Scenario: {scenario}. "
        f"Reply in {language} using 1-3 short sentences. "
        "End with a question to continue the conversation. "
        "Gently correct the learner's latest message. "
        'Reply ONLY as JSON: '
        '{"reply": str, "english": str, "correction": str}. '
        "Use an empty correction string if the message is correct."
    )

    return _chat(
        system,
        messages=history,
        json_mode=True,
        temperature=0.7
    )


# --------------------------------------------------
# SPEECH-TO-TEXT
# --------------------------------------------------

def transcribe(audio_bytes, language_code=None):
    """
    Convert recorded speech into text using Groq.

    Args:
        audio_bytes: Recorded audio file in bytes.
        language_code: Optional language code.
                       If None, automatic language detection is used.

    Returns:
        Recognized text as a string.
    """

    if not audio_bytes:
        raise AIError(
            "No audio recorded. Please record your voice."
        )

    try:

        kwargs = {}

        # Specify language only when provided.
        # Otherwise, Whisper automatically detects language.

        if language_code:
            kwargs["language"] = language_code.split("-")[0]

        response = _client().audio.transcriptions.create(

            file=(
                "speech.wav",
                audio_bytes,
                "audio/wav"
            ),

            model=STT_MODEL,

            response_format="json",

            **kwargs
        )

        transcript = (
            response.text or ""
        ).strip()

        if not transcript:
            raise AIError(
                "No speech detected. Please speak clearly and try again."
            )

        return transcript

    except AIError:
        raise

    except Exception as e:

        raise AIError(
            f"Voice recognition failed: {e}"
        )


# --------------------------------------------------
# END OF AI MODULE
# --------------------------------------------------
