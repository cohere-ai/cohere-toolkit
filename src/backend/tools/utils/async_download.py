import asyncio
import functools
from typing import List

import aiohttp

from backend.services.logger.utils import LoggerFactory

TIMEOUT = aiohttp.ClientTimeout(total=120)

logger = LoggerFactory().get_logger()


def sync_perform(id_to_urls: List[str], access_token: str) -> dict[str, str]:
    return asyncio.run(_download_files(id_to_urls, access_token))


async def async_perform(id_to_urls: List[str], access_token: str) -> dict[str, str]:
    return await _download_files(id_to_urls, access_token)


async def _download_files(
    id_to_urls: dict[str, str], access_token: str
) -> dict[str, str]:
    async with aiohttp.ClientSession() as session:
        tasks = [
            _download(session, id, url, access_token)
            for (id, url) in id_to_urls.items()
        ]
        id_to_texts = await asyncio.gather(*tasks)
        return functools.reduce(lambda x, y: x | y, id_to_texts)


async def _download(
    session: aiohttp.ClientSession, id: str, url: str, access_token: str
):
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        async with session.get(url, headers=headers, timeout=TIMEOUT) as response:
            return {id: await response.text()}
    except Exception as error:
        logger.error(
            event="[Async Download]: Error fetching url",
            url=url,
            error=error,
        )
        return {}
