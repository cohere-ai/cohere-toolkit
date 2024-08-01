import httpx
from dotenv import load_dotenv

from backend.config.settings import Settings
from backend.services.compass import Compass

load_dotenv()


class Configuration:
    # TODO: Env vars checking needs to happen here
    # Skipping for now for simplicity
    COMPASS: Compass = Compass(
        compass_api_url=Settings().compass.api_url,
        compass_parser_url=Settings().compass.parser_url,
        compass_username=Settings().compass.username,
        compass_password=Settings().compass.password,
    )

    HTTPX_CLIENT: httpx.Client = httpx.Client(http2=True, timeout=300)
