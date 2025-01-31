from typing import Any

import requests

from backend.config.settings import Settings
from backend.database_models.database import get_session
from backend.schemas.context import Context
from backend.schemas.tool import ToolCategory, ToolDefinition
from backend.services.logger.utils import LoggerFactory
from backend.tools.base import BaseTool, ToolAuthException
from backend.tools.sharepoint.auth import SharepointAuth
from backend.tools.sharepoint.constants import SEARCH_LIMIT, SHAREPOINT_TOOL_ID
from backend.tools.sharepoint.utils import serialize_file_contents, serialize_metadata

logger = LoggerFactory().get_logger()


class SharepointTool(BaseTool):
    ID = SHAREPOINT_TOOL_ID
    SHAREPOINT_TENANT_ID = Settings().get('tools.sharepoint.tenant_id')
    SHAREPOINT_CLIENT_ID = Settings().get('tools.sharepoint.client_id')
    SHAREPOINT_CLIENT_SECRET = Settings().get('tools.sharepoint.client_secret')

    BASE_URL = "https://graph.microsoft.com/v1.0"
    SEARCH_ENTITY_TYPES = ["driveItem"]
    DRIVE_ITEM_DATA_TYPE = "#microsoft.graph.driveItem"

    @classmethod
    def is_available(cls) -> bool:
        return all([
            cls.SHAREPOINT_TENANT_ID,
            cls.SHAREPOINT_CLIENT_ID,
            cls.SHAREPOINT_CLIENT_SECRET,
        ])


    @classmethod
    def get_tool_definition(cls) -> ToolDefinition:
        return ToolDefinition(
            name=cls.ID,
            display_name="Sharepoint",
            implementation=cls,
            parameter_definitions={
                "query": {
                    "description": "Query to search Sharepoint documents with.",
                    "type": "str",
                    "required": True,
                }
            },
            is_visible=True,
            is_available=SharepointTool.is_available(),
            auth_implementation=SharepointAuth,
            should_return_token=True,
            error_message=cls.generate_error_message(),
            category=ToolCategory.DataLoader,
            description="Returns a list of relevant document snippets from the user's Sharepoint.",
        ) # type: ignore

    def _prepare_auth(self, user_id: str) -> None:
        sharepoint_auth = SharepointAuth()
        session = next(get_session())
        if sharepoint_auth.is_auth_required(session, user_id=user_id):
            session.close()
            raise ToolAuthException(
                "Sharepoint Tool auth Error: Agent creator credentials need to re-authenticate",
                SHAREPOINT_TOOL_ID,
            )

        access_token = sharepoint_auth.get_token(session, user_id)
        self.headers = {
            "Authorization": f"Bearer {access_token}"
        }

    def search(self, query: str) -> list[dict]:
        request = {
            "entityTypes": self.SEARCH_ENTITY_TYPES,
            "query": {
                "queryString": query,
                "size": SEARCH_LIMIT,
            },
        }

        error_message = "Error while searching with Sharepoint Tool"
        try:
            response = requests.post(
                f"{self.BASE_URL}/search/query",
                headers=self.headers,
                json={"requests": [request]},
            )
            body = response.json()
        except Exception as exc:
            logger.error(event=f"[Sharepoint] Search error: {exc}")
            raise Exception(error_message) from exc
        if not response.ok:
            error = body.get("error", {})
            error_code = error.get("code")
            error_description = error.get("message")
            error_message = f"{error_message}: {error_code}. {error_description}"
            logger.error(event=f"[Sharepoint] Search error: {error_message}")
            raise  Exception(error_message)

        if not body.get("value"):
            return []

        return body["value"][0].get("hitsContainers", [])

    def get_drive_item_content(self, parent_drive_id: str, resource_id: str) -> bytes|None:
        response = requests.get(
            f"{self.BASE_URL}/drives/{parent_drive_id}/items/{resource_id}/content",
            headers=self.headers,
        )

        # Fail gracefully when retrieving content
        if not response.ok:
            return None

        return response.content

    def collect_items(self, hits: list[dict]) -> list:
        # Gather data
        drive_items = []
        for hit in hits:
            if hit["resource"]["@odata.type"] == self.DRIVE_ITEM_DATA_TYPE:
                parent_drive_id = hit["resource"]["parentReference"]["driveId"]
                resource_id = hit["resource"]["id"]
                drive_item = self.get_drive_item_content(
                    parent_drive_id, resource_id
                )

                if drive_item:
                    drive_items.append((hit, drive_item))

        return drive_items


    async def call(
        self, parameters: dict, ctx: Context, **kwargs: Any,
    ) -> list[dict[str, Any]]:
        user_id = str(kwargs.get("user_id", ""))
        self._prepare_auth(user_id)
        query = parameters.get("query", "").replace("'", "\\'")
        search_response = self.search(query)

        hits = []
        for hit_container in search_response:
            hits.extend(hit_container.get("hits", []))

        drive_items = self.collect_items(hits)

        # Serialize results
        results = []
        for hit, content in drive_items:
            result = {}
            if (resource := hit.get("resource")) is not None:
                result.update(**serialize_metadata(resource))

            content = serialize_file_contents(content, result.get("name", ""))
            result.update({
                "text": content,
            })
            results.append(result)

        if not results:
            logger.info(event="[Sharepoint] No documents found.")
            return self.get_no_results_error()

        return results
