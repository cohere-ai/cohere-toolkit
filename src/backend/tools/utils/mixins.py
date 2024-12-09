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
