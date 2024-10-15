from google.cloud.texttospeech import (
    AudioConfig,
    AudioEncoding,
    SynthesisInput,
    TextToSpeechClient,
    VoiceSelectionParams,
)
from googleapiclient.discovery import build

from backend.config import Settings


def synthesize(text: str) -> bytes:
    """
    Synthesizes speech from the input text.

    Args:
        text (str): The input text to be synthesized into speech.

    Returns:
        bytes: The audio content generated from the input text in MP3 format.
    """
    client = TextToSpeechClient(client_options={
        "api_key": Settings().google_cloud.api_key
    })

    language = detect_language(text)

    response = client.synthesize_speech(
        input=SynthesisInput(text=text),
        voice=VoiceSelectionParams(language_code=language),
        audio_config=AudioConfig(audio_encoding=AudioEncoding.MP3)
    )

    return response.audio_content


def detect_language(text: str) -> str:
    """
    Detect the language of the given text.

    Args:
        text (str): The text for which the language needs to be detected.

    Returns:
        str: The language code of the detected language (e.g., 'en', 'es').
    """
    client = build("translate", "v2", developerKey=Settings().google_cloud.api_key)

    response = client.detections().list(q=text).execute()

    return response["detections"][0][0]["language"]
