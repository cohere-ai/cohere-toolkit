from backend.crud import agent_tool_metadata as agent_tool_metadata_crud
from backend.database_models.database import DBSessionDep
from backend.schemas.agent import AgentToolMetadataArtifactsType
from backend.schemas.context import Context
from backend.services.auth.crypto import encrypt
from backend.services.cache import cache_get_dict, cache_put


class ToolAuthenticationCacheMixin:
    def insert_tool_auth_cache(self, user_id: str, tool_id: str) -> str:
        """
        Generates a token from a composite string formed by user_id + tool_id, and stores it in
        cache.
        """
        value = user_id + tool_id
        # Encrypt value with Fernet and convert to string
        key = encrypt(value).decode()

        # Existing cache entry
        if cache_get_dict(key):
            return key

        payload = {"user_id": user_id, "tool_id": tool_id}
        cache_put(key, payload)

        return key


class WebSearchFilteringMixin:
    def get_filters(
        self,
        filter_type: AgentToolMetadataArtifactsType,
        session: DBSessionDep,
        ctx: Context,
    ) -> list[str]:
        agent_id = ctx.get_agent_id()
        user_id = ctx.get_user_id()

        if not agent_id or not user_id:
            return []

        agent_tool_metadata = agent_tool_metadata_crud.get_agent_tool_metadata(
            db=session,
            agent_id=agent_id,
            tool_name=self.ID,
            user_id=user_id,
        )

        if not agent_tool_metadata:
            return []

        return [
            artifact[filter_type]
            for artifact in agent_tool_metadata.artifacts
            if filter_type in artifact
        ]
