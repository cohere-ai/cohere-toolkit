from typing import Any, Dict, List

from google.auth.exceptions import RefreshError

from backend.config.settings import Settings
from backend.crud import tool_auth as tool_auth_crud
from backend.services.compass import Compass
from backend.services.logger.utils import LoggerFactory
from backend.tools.base import BaseTool
from backend.tools.google_drive.constants import GOOGLE_DRIVE_TOOL_ID, SEARCH_LIMIT

logger = LoggerFactory().get_logger()


class GoogleDrive(BaseTool):
    """
    Tool that searches Google Drive
    """

    NAME = GOOGLE_DRIVE_TOOL_ID

    CLIENT_ID = Settings().tools.google_drive.client_id
    CLIENT_SECRET = Settings().tools.google_drive.client_secret

    @classmethod
    def is_available(cls) -> bool:
        return cls.CLIENT_ID is not None and cls.CLIENT_SECRET is not None

    def _handle_tool_specific_errors(cls, error: Exception, **kwargs: Any):
        message = "[Google Drive] Tool Error: {}".format(str(error))

        if isinstance(error, RefreshError):
            session = kwargs["session"]
            user_id = kwargs["user_id"]
            tool_auth_crud.delete_tool_auth(
                db=session, user_id=user_id, tool_id=GOOGLE_DRIVE_TOOL_ID
            )

        logger.error(
            event="[Google Drive] Auth token error: Please refresh the page and re-authenticate."
        )
        raise Exception(message)

    async def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:
        user_id = kwargs.get("user_id")
        agent_id = kwargs["agent_id"]
        index_name = "{}_{}".format(
            agent_id if agent_id is not None else user_id, GOOGLE_DRIVE_TOOL_ID
        )
        query = parameters.get("query", "").replace("'", "\\'")

        compass = None
        try:
            compass = Compass(
                compass_api_url=Settings().compass.api_url,
                compass_parser_url=Settings().compass.parser_url,
                compass_username=Settings().compass.username,
                compass_password=Settings().compass.password,
            )
        except Exception:
            pass

        if compass is not None:
            # Compass setup found
            # Query Compass
            documents = []
            documents = compass.invoke(
                compass.ValidActions.SEARCH,
                {
                    "index": index_name,
                    "query": query,
                    # TODO filter on permissions
                },
            )
            if documents.error:
                raise Exception(f"Compass no documents found for search query {query}")

            hits = documents.result["hits"]
            chunks = sorted(
                [
                    {
                        "text": chunk["content"]["text"],
                        "score": chunk["score"],
                        "url": hit["content"].get("url", ""),
                        "title": hit["content"].get("title", ""),
                    }
                    for hit in hits
                    for chunk in hit["chunks"]
                ],
                key=lambda x: x["score"],
                reverse=True,
            )[:SEARCH_LIMIT]
            if chunks == []:
                raise Exception(f"Compass no documents found for search query {query}")
            return chunks
        else:
            # No compass setup
            # Default to raw gdrive search
            logger.info(event="[Google Drive] Defaulting to raw Google Drive search.")
            agent_tool_metadata = kwargs["agent_tool_metadata"]
            documents = await _default_gdrive_list_files(
                user_id=user_id, query=query, agent_tool_metadata=agent_tool_metadata
            )
            return documents


async def _default_gdrive_list_files(
    user_id: str, query: str, agent_tool_metadata: Dict[str, str]
):
    from backend.tools.google_drive.constants import (
        DOC_FIELDS,
        NATIVE_SEARCH_MIME_TYPES,
        SEARCH_MIME_TYPES,
    )
    from backend.tools.google_drive.sync.utils import (
        extract_export_link,
        extract_title,
        extract_web_view_link,
        get_service,
        perform_get_batch,
        process_shortcut_file,
    )
    from backend.tools.utils import async_download

    (service, creds) = (
        get_service(api="drive", user_id=user_id)[key] for key in ("service", "creds")
    )
    conditions = [
        "("
        + " or ".join([f"mimeType = '{mime_type}'" for mime_type in SEARCH_MIME_TYPES])
        + ")",
        "("
        + " or ".join([f"fullText contains '{word}'" for word in [query]])
        + " or "
        + " or ".join([f"name contains '{word}'" for word in [query]])
        + ")",
    ]

    file_ids = []
    folder_ids = []
    if agent_tool_metadata:
        for metadata in agent_tool_metadata:
            if metadata.tool_name == GOOGLE_DRIVE_TOOL_ID:
                artifacts = metadata.artifacts
                for artifact in artifacts:
                    if artifact["type"] == "folder":
                        folder_ids.append(artifact["id"])
                    else:
                        file_ids.append(artifact["id"])

    # Condition on files if exist
    files = []
    if file_ids:
        files = perform_get_batch(file_ids=file_ids, user_id=user_id)
    else:
        # Condition on folders if exist
        if folder_ids:
            # Explanation: https://stackoverflow.com/questions/78063848/google-drive-api-full-text-search-doesnt-work-when-using-in-parents-option#comment138803743_78063848
            if len(folder_ids) == 1:
                folder_ids += folder_ids
            conditions.append(
                "("
                + " or ".join(
                    ["'{}' in parents".format(folder_id) for folder_id in folder_ids]
                )
                + ")"
            )

        q = " and ".join(conditions)
        fields = f"nextPageToken, files({DOC_FIELDS})"

        search_results = []
        try:
            search_results = (
                service.files()
                .list(
                    pageSize=SEARCH_LIMIT,
                    q=q,
                    includeItemsFromAllDrives=True,
                    supportsAllDrives=True,
                    fields=fields,
                )
                .execute()
            )
        except Exception as error:
            logger.error(event="[Google Drive] Error searching files", error=error)

        files = search_results.get("files", [])
        if not files:
            logger.info(event="[Google Drive] No files found.")

    if not files:
        return []

    # post process files
    processed_files = {x["id"]: process_shortcut_file(service, x) for x in files}
    web_view_links = {x["id"]: extract_web_view_link(x) for x in files}
    titles = {x["id"]: extract_title(x) for x in files}

    id_to_texts = {}

    # native files
    native_files = {
        file_id: x
        for file_id, x in processed_files.items()
        if x["mimeType"] in NATIVE_SEARCH_MIME_TYPES
    }
    id_to_urls = {
        file_id: extract_export_link(x) for file_id, x in native_files.items()
    }
    if id_to_urls:
        id_to_texts = await async_download.async_perform(id_to_urls, creds.token)

    return [
        {
            "text": id_to_texts[idd],
            "url": web_view_links.get(idd, ""),
            "title": titles.get(idd, ""),
        }
        for idd in id_to_texts
    ]
