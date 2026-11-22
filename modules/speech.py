"""Text-to-speech via gTTS."""
import io
from gtts import gTTS


class SpeechError(Exception):
    pass


def speak(text: str, lang: str) -> bytes:
    if not text.strip():
        raise SpeechError("Nothing to read aloud.")
    try:
        buf = io.BytesIO()
        gTTS(text=text[:3000], lang=lang).write_to_fp(buf)
        return buf.getvalue()
    except Exception as e:
        raise SpeechError(f"Text-to-speech unavailable for this language or network: {e}")
