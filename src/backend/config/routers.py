from enum import StrEnum

from fastapi import Depends

from backend.config import env
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
    SNAPSHOT = "snapshot"


# Router dependency mappings
ROUTER_DEPENDENCIES = {
    RouterName.AUTH: {
        "default": [
            Depends(env),
        ],
        "auth": [
            Depends(env),
        ],
    },
    RouterName.CHAT: {
        "default": [
            Depends(env),
            Depends(validate_user_header),
            Depends(validate_chat_request),
        ],
        "auth": [
            Depends(env),
            Depends(validate_chat_request),
            Depends(validate_authorization),
        ],
    },
    RouterName.CONVERSATION: {
        "default": [
            Depends(env),
            Depends(validate_user_header),
        ],
        "auth": [
            Depends(env),
            Depends(validate_authorization),
        ],
    },
    RouterName.DEPLOYMENT: {
        "default": [
            Depends(env),
        ],
        "auth": [
            Depends(env),
            Depends(validate_authorization),
        ],
    },
    RouterName.EXPERIMENTAL_FEATURES: {
        "default": [
            Depends(env),
        ],
        "auth": [
            Depends(env),
            Depends(validate_authorization),
        ],
    },
    RouterName.TOOL: {
        "default": [
            Depends(env),
        ],
        "auth": [
            Depends(env),
            Depends(validate_authorization),
        ],
    },
    RouterName.USER: {
        "default": [
            Depends(env),
        ],
        "auth": [
            # TODO: Remove auth only for create user endpoint
            Depends(env),
        ],
    },
    RouterName.AGENT: {
        "default": [
            Depends(env),
        ],
        "auth": [
            Depends(env),
            # TODO: Add if the router's have to have authorization
            # Depends(validate_authorization),
        ],
    },
    RouterName.SNAPSHOT: {
        "default": [
            Depends(env),
            Depends(validate_user_header),
        ],
        "auth": [
            Depends(env),
            Depends(validate_authorization),
        ],
    },
}
