from concurrent import futures

import httpx

from backend.services.logger.utils import LoggerFactory

logger = LoggerFactory().get_logger()


def perform_batch(
    httpx_client: httpx.Client, id_to_urls: dict[str, str], access_token: str
) -> dict[str, str]:
    texts = []
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures_list = [
            executor.submit(_download, httpx_client, id, url, access_token)
            for (id, url) in id_to_urls.items()
        ]
        for future in futures.as_completed(futures_list):
            try:
                texts.append(future.result())
            except Exception as e:
                raise e

    return texts


def perform_single(httpx_client: httpx.Client, url: str, access_token: str) -> str:
    return _download(httpx_client=httpx_client, url=url, access_token=access_token)


def _download(httpx_client: httpx.Client, url: str, access_token: str):
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = httpx_client.get(url, headers=headers, follow_redirects=True)
        response = response.text
        return response
    except Exception as error:
        logger.error("Error fetching", url=url, error=error)
        return ""
