import httpx
from dotenv import load_dotenv

load_dotenv()


class Configuration:
    HTTPX_CLIENT: httpx.Client = httpx.Client(http2=True, timeout=300)
