
"""GlobeTalk translation with Google Translator and MyMemory fallback."""

from deep_translator import GoogleTranslator, MyMemoryTranslator
from langdetect import detect, DetectorFactory
from .config import LANGS

DetectorFactory.seed = 0

MAX = 4500


class TranslationError(Exception):
    pass


# Supported GlobeTalk language codes
SUPPORTED_CODES = {
    code.lower(): code
    for code in LANGS.values()
}


# Regional codes required by MyMemory
MYMEMORY_CODES = {
    "en": "en-GB",
    "es": "es-ES",
    "fr": "fr-FR",
    "de": "de-DE",
    "it": "it-IT",
    "pt": "pt-PT",
    "hi": "hi-IN",
    "ta": "ta-IN",
    "te": "te-IN",
    "ml": "ml-IN",
    "bn": "bn-IN",
    "ar": "ar-SA",
    "ru": "ru-RU",
    "ja": "ja-JP",
    "ko": "ko-KR",
    "zh-cn": "zh-CN",
    "tr": "tr-TR",
    "nl": "nl-NL",
    "th": "th-TH",
    "id": "id-ID",
}


LANGUAGE_ALIASES = {
    "zh-tw": "zh-CN",
    "zh-cn": "zh-CN",
}


def normalize_code(code):
    """Normalize language codes."""

    if not code:
        return None

    code = LANGUAGE_ALIASES.get(code.lower(), code)

    return SUPPORTED_CODES.get(code.lower())


def detect_language(text: str) -> str:
    """Detect the source language."""

    text = (text or "").strip()

    if not text:
        raise TranslationError(
            "Please speak or enter some text first."
        )

    try:
        detected = detect(text).lower()

        normalized = normalize_code(detected)

        if normalized:
            return normalized

        # Fallback for uncertain or unsupported detection
        return "en"

    except Exception:
        return "en"


def _chunks(text: str):
    """Split long text into smaller chunks."""

    parts = []
    current = ""

    for line in text.split("\n"):

        while len(line) > MAX:

            if current:
                parts.append(current)
                current = ""

            parts.append(line[:MAX])
            line = line[MAX:]

        if len(current) + len(line) + 1 > MAX:

            if current:
                parts.append(current)

            current = line

        else:
            current = (
                f"{current}\n{line}"
                if current else line
            )

    if current:
        parts.append(current)

    return parts


def translate(text: str, src: str, tgt: str) -> str:
    """Translate using Google first and MyMemory as fallback."""

    text = (text or "").strip()

    if not text:
        raise TranslationError(
            "Please enter or speak some text first."
        )

    source = normalize_code(src)
    target = normalize_code(tgt)

    if not source:
        raise TranslationError(
            f"Unsupported source language: {src}"
        )

    if not target:
        raise TranslationError(
            f"Unsupported target language: {tgt}"
        )

    if source.lower() == target.lower():
        return text

    translated_parts = []

    for part in _chunks(text):

        if not part.strip():
            translated_parts.append(part)
            continue

        google_error = None
        memory_error = None

        # 1. Try Google Translator
        try:
            result = GoogleTranslator(
                source=source,
                target=target
            ).translate(part)

            if result:
                translated_parts.append(result)
                continue

            google_error = "Google returned an empty result."

        except Exception as error:
            google_error = str(error)

        # 2. Try MyMemory using regional language codes
        try:
            memory_source = MYMEMORY_CODES.get(
                source.lower()
            )

            memory_target = MYMEMORY_CODES.get(
                target.lower()
            )

            if not memory_source or not memory_target:
                raise ValueError(
                    "Regional language code is unavailable."
                )

            result = MyMemoryTranslator(
                source=memory_source,
                target=memory_target
            ).translate(part)

            if result:
                translated_parts.append(result)
                continue

            memory_error = "MyMemory returned an empty result."

        except Exception as error:
            memory_error = str(error)

        # Both services failed
        raise TranslationError(
            "Both translation services failed.\n\n"
            f"Google error: {google_error}\n\n"
            f"MyMemory error: {memory_error}"
        )

    return "\n".join(translated_parts)
