import time
from typing import Any, Dict, List

from fastapi import HTTPException
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from backend.config.settings import Settings
from backend.crud import tool_auth as tool_auth_crud
from backend.services.compass import Compass
from backend.services.logger.utils import LoggerFactory
from backend.tools.base import BaseTool
from backend.tools.utils import async_download, parallel_get_files

from .constants import (
    COMPASS_UPDATE_INTERVAL,
    DOC_FIELDS,
    GOOGLE_DRIVE_TOOL_ID,
    NATIVE_SEARCH_MIME_TYPES,
    NON_NATIVE_SEARCH_MIME_TYPES,
    SEARCH_LIMIT,
    SEARCH_MIME_TYPES,
)
from .utils import (
    extract_links,
    extract_titles,
    extract_web_view_links,
    non_native_files_perform,
    process_shortcut_files,
)

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
        return cls.CLIENT_ID is not None and cls.CLIENT_ID is not None

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
        session = kwargs.get("session")
        user_id = kwargs.get("user_id")
        agent_id = kwargs["agent_id"]
        agent_tool_metadata = kwargs["agent_tool_metadata"]
        index_name = "{}_{}".format(
            agent_id if agent_id is not None else user_id, GOOGLE_DRIVE_TOOL_ID
        )
        query = parameters.get("query", "").replace("'", "\\'")
        conditions = [
            "("
            + " or ".join(
                [f"mimeType = '{mime_type}'" for mime_type in SEARCH_MIME_TYPES]
            )
            + ")",
            "("
            + " or ".join([f"fullText contains '{word}'" for word in [query]])
            + " or "
            + " or ".join([f"name contains '{word}'" for word in [query]])
            + ")",
        ]

        tool_auth = tool_auth_crud.get_tool_auth(
            db=session, tool_id=GOOGLE_DRIVE_TOOL_ID, user_id=user_id
        )

        if not tool_auth:
            error_message = f"[Google Drive] Error searching Google Drive: Could not find ToolAuth with tool_id: {self.NAME} and user_id: {kwargs.get('user_id')}"
            logger.error(event=error_message)
            raise HTTPException(status_code=401, detail=error_message)

        creds = Credentials(tool_auth.access_token)

        # parse tool metadata
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
        service = build("drive", "v3", credentials=creds)
        if file_ids:
            files = parallel_get_files.perform(file_ids=file_ids, creds=creds)
        else:
            # Condition on folders if exist
            if folder_ids:
                # Explanation: https://stackoverflow.com/questions/78063848/google-drive-api-full-text-search-doesnt-work-when-using-in-parents-option#comment138803743_78063848
                if len(folder_ids) == 1:
                    folder_ids += folder_ids
                conditions.append(
                    "("
                    + " or ".join(
                        [
                            "'{}' in parents".format(folder_id)
                            for folder_id in folder_ids
                        ]
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
            except Exception as e:
                self._handle_tool_specific_errors(
                    error=e, **{"session": session, "user_id": user_id}
                )

            files = search_results.get("files", [])
            if not files:
                logger.debug(event="[Google Drive] No files found.")
        if not files:
            return []

        # post process files
        processed_files = process_shortcut_files(service, files)
        web_view_links = extract_web_view_links(processed_files)
        titles = extract_titles(processed_files)

        id_to_texts = {}

        # native files
        native_files = [
            x for x in processed_files if x["mimeType"] in NATIVE_SEARCH_MIME_TYPES
        ]
        id_to_urls = extract_links(native_files)
        if id_to_urls:
            id_to_texts = await async_download.async_perform(id_to_urls, creds.token)

        # initialize Compass
        compass = None
        try:
            compass = Compass()
        except Exception as e:
            # Compass is not available. Using without Compass
            logger.info(event=f"[Google Drive] Error initializing Compass: {str(e)}")
            return [
                {
                    "text": id_to_texts[idd],
                    "url": web_view_links.get(idd, ""),
                    "title": titles.get(idd, ""),
                }
                for idd in id_to_texts
            ]

        # non-native files
        non_native_files = [
            x for x in processed_files if x["mimeType"] in NON_NATIVE_SEARCH_MIME_TYPES
        ]
        non_native_results = await non_native_files_perform(
            service=service, compass=compass, files=non_native_files
        )
        id_to_texts = {
            **id_to_texts,
            **non_native_results,
        }

        if not id_to_texts:
            return []

        """
        Compass logic
        """
        # idempotent create index
        compass.invoke(
            action=Compass.ValidActions.CREATE_INDEX,
            parameters={"index": index_name},
        )

        # handle creation/update of each file
        for file_id in id_to_texts:
            fetched_doc = None
            try:
                fetched_doc = compass.invoke(
                    action=Compass.ValidActions.GET_DOCUMENT,
                    parameters={"index": index_name, "file_id": file_id},
                ).result["doc"]
                url = fetched_doc["content"].get("url")
                title = fetched_doc["content"].get("title")
                last_updated = fetched_doc["content"].get("last_updated")

                should_update = False
                if last_updated is None or url is None or title is None:
                    should_update = True
                else:
                    if int(time.time()) - last_updated > COMPASS_UPDATE_INTERVAL:
                        should_update = True

                # doc update if needed
                if should_update:
                    # update
                    compass.invoke(
                        action=Compass.ValidActions.UPDATE,
                        parameters={
                            "index": index_name,
                            "file_id": file_id,
                            "file_text": id_to_texts[file_id],
                        },
                    )
                    # add context
                    compass.invoke(
                        action=Compass.ValidActions.ADD_CONTEXT,
                        parameters={
                            "index": index_name,
                            "file_id": file_id,
                            "context": {
                                "url": web_view_links[file_id],
                                "title": titles[file_id],
                                "last_updated": int(time.time()),
                            },
                        },
                    )
                    # refresh
                    compass.invoke(
                        action=Compass.ValidActions.REFRESH,
                        parameters={"index": index_name},
                    )
            except Exception:
                # create
                compass.invoke(
                    action=Compass.ValidActions.CREATE,
                    parameters={
                        "index": index_name,
                        "file_id": file_id,
                        "file_text": id_to_texts[file_id],
                    },
                )
                # add context
                compass.invoke(
                    action=Compass.ValidActions.ADD_CONTEXT,
                    parameters={
                        "index": index_name,
                        "file_id": file_id,
                        "context": {
                            "url": web_view_links[file_id],
                            "title": titles[file_id],
                            "last_updated": int(time.time()),
                        },
                    },
                )
                # refresh
                compass.invoke(
                    action=Compass.ValidActions.REFRESH,
                    parameters={"index": index_name},
                )

        # fetch documents from index
        hits = compass.invoke(
            action=Compass.ValidActions.SEARCH,
            parameters={
                "index": index_name,
                "query": query,
                "top_k": SEARCH_LIMIT,
            },
        ).result["hits"]
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

        return chunks
