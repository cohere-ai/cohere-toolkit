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

    Raises:
        ValueError: If the Google Cloud API key from the settings is not valid.
    """
    client = TextToSpeechClient(client_options={
        "api_key": _validate_google_cloud_api_key()
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

    Raises:
        ValueError: If the Google Cloud API key from the settings is not valid.
    """
    client = build("translate", "v2", developerKey=_validate_google_cloud_api_key())

    response = client.detections().list(q=text).execute()

    return response["detections"][0][0]["language"]


def _validate_google_cloud_api_key() -> str:
    """
    Validates the Google Cloud API key from the settings.

    Returns:
        str: The validated API key.

    Raises:
        ValueError: If the API key is not found in the settings or is empty.
    """
    google_cloud = Settings().get('google_cloud')

    if not google_cloud:
        raise ValueError("google_cloud in secrets.yaml is missing.")

    if not google_cloud.api_key:
        raise ValueError("google_cloud.api_key in secrets.yaml is missing.")

    return google_cloud.api_key
