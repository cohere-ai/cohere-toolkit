from enum import StrEnum

from fastapi import Depends

from backend.database_models import get_session
from backend.services.auth.request_validators import validate_authorization
from backend.services.request_validators import (
    validate_chat_request,
    validate_user_header,
)


# Important! Any new routers must have a corresponding RouterName entry and Router dependencies
# mapping below. Make sure they use the correct ones depending on whether authentication is enabled or not.
class RouterName(StrEnum):
    AUTH = "auth"
    CHAT = "chat"
    CONVERSATION = "conversation"
    DEPLOYMENT = "deployment"
    EXPERIMENTAL_FEATURES = "experimental_features"
    TOOL = "tool"
    USER = "user"
    AGENT = "agent"
    DEFAULT_AGENT = "default_agent"
    SNAPSHOT = "snapshot"
    MODEL = "model"


# Router dependency mappings
ROUTER_DEPENDENCIES = {
    RouterName.AUTH: {
        "default": [
            Depends(get_session),
        ],
        "auth": [
            Depends(get_session),
        ],
    },
    RouterName.CHAT: {
        "default": [
            Depends(get_session),
            Depends(validate_user_header),
            Depends(validate_chat_request),
        ],
        "auth": [
            Depends(get_session),
            Depends(validate_chat_request),
            Depends(validate_authorization),
        ],
    },
    RouterName.CONVERSATION: {
        "default": [
            Depends(get_session),
            Depends(validate_user_header),
        ],
        "auth": [
            Depends(get_session),
            Depends(validate_authorization),
        ],
    },
    RouterName.DEPLOYMENT: {
        "default": [
            Depends(get_session),
        ],
        "auth": [
            Depends(get_session),
            Depends(validate_authorization),
        ],
    },
    RouterName.EXPERIMENTAL_FEATURES: {
        "default": [
            Depends(get_session),
        ],
        "auth": [
            Depends(get_session),
            Depends(validate_authorization),
        ],
    },
    RouterName.TOOL: {
        "default": [
            Depends(get_session),
        ],
        "auth": [
            Depends(get_session),
            Depends(validate_authorization),
        ],
    },
    RouterName.USER: {
        "default": [
            Depends(get_session),
        ],
        "auth": [
            # TODO: Remove auth only for create user endpoint
            Depends(get_session),
        ],
    },
    RouterName.AGENT: {
        "default": [
            Depends(get_session),
        ],
        "auth": [
            Depends(get_session),
            Depends(validate_authorization),
        ],
    },
    RouterName.DEFAULT_AGENT: {
        "default": [
            Depends(get_session),
        ],
        "auth": [
            Depends(get_session),
            Depends(validate_authorization),
        ],
    },
    RouterName.SNAPSHOT: {
        "default": [
            Depends(get_session),
            Depends(validate_user_header),
        ],
        "auth": [
            Depends(get_session),
            Depends(validate_authorization),
        ],
    },
    RouterName.MODEL: {
        "default": [
            Depends(get_session),
        ],
        "auth": [
            Depends(get_session),
            Depends(validate_authorization),
        ],
    },
}
