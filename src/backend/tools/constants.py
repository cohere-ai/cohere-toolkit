from aiohttp import ClientTimeout

TIMEOUT_SECONDS = 15
ASYNC_TIMEOUT = ClientTimeout(total=TIMEOUT_SECONDS)
