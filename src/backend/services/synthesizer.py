from typing import Any, Generator

from googletrans import Translator
from gtts import gTTS


def synthesize_stream(text: str) -> Generator[bytes, Any, Any]:
    """
    Generate a stream of audio bytes from the given text using text-to-speech synthesis.

    Args:
        text (str): The input text to be synthesized into speech.

    Returns:
        Generator[bytes, Any, Any]: A generator yielding audio bytes of the synthesized speech.
    """
    lang = detect_language(text)
    tts = gTTS(text, lang=lang, slow=False)
    return tts.stream()


def detect_language(text: str) -> str:
    """
    Detect the language of the given text.

    Args:
        text (str): The text for which the language needs to be detected.

    Returns:
        str: The language code of the detected language (e.g., 'en', 'es').
    """
    for char in text:
        if char.isalpha() and not char.isascii():
            return Translator().detect(text).lang
    return "en"
