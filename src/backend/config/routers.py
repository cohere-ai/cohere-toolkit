from enum import StrEnum

from fastapi import Depends

from backend.database_models import get_session
from backend.services.auth.request_validators import (
    ScimAuthValidation,
    validate_authorization,
)
from backend.services.request_validators import (
    validate_chat_request,
    validate_organization_header,
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
    ORGANIZATION = "organization"
    TOOL = "tool"
    USER = "user"
    AGENT = "agent"
    SNAPSHOT = "snapshot"
    MODEL = "model"
    SCIM = "scim"


class DependencyType(StrEnum):
    DEFAULT = "default"
    AUTH = "auth"


# Router dependency mappings
ROUTER_DEPENDENCIES = {
    RouterName.AUTH: {
        DependencyType.DEFAULT: [
            Depends(get_session),
            Depends(validate_organization_header),
        ],
        DependencyType.AUTH: [
            Depends(get_session),
            Depends(validate_organization_header),
        ],
    },
    RouterName.CHAT: {
        DependencyType.DEFAULT: [
            Depends(get_session),
            Depends(validate_user_header),
            Depends(validate_chat_request),
            Depends(validate_organization_header),
        ],
        DependencyType.AUTH: [
            Depends(get_session),
            Depends(validate_chat_request),
            Depends(validate_authorization),
            Depends(validate_organization_header),
        ],
    },
    RouterName.CONVERSATION: {
        DependencyType.DEFAULT: [
            Depends(get_session),
            Depends(validate_user_header),
            Depends(validate_organization_header),
        ],
        DependencyType.AUTH: [
            Depends(get_session),
            Depends(validate_authorization),
            Depends(validate_organization_header),
        ],
    },
    RouterName.DEPLOYMENT: {
        DependencyType.DEFAULT: [
            Depends(get_session),
            Depends(validate_organization_header),
        ],
        DependencyType.AUTH: [
            Depends(get_session),
            Depends(validate_authorization),
            Depends(validate_organization_header),
        ],
    },
    RouterName.EXPERIMENTAL_FEATURES: {
        DependencyType.DEFAULT: [
            Depends(get_session),
            Depends(validate_organization_header),
        ],
        DependencyType.AUTH: [
            Depends(get_session),
            Depends(validate_authorization),
            Depends(validate_organization_header),
        ],
    },
    RouterName.ORGANIZATION: {
        DependencyType.DEFAULT: [
            Depends(get_session),
            Depends(validate_organization_header),
        ],
        DependencyType.AUTH: [
            Depends(get_session),
            Depends(validate_authorization),
            Depends(validate_organization_header),
        ],
    },
    RouterName.TOOL: {
        DependencyType.DEFAULT: [
            Depends(get_session),
            Depends(validate_organization_header),
        ],
        DependencyType.AUTH: [
            Depends(get_session),
            Depends(validate_authorization),
            Depends(validate_organization_header),
        ],
    },
    RouterName.USER: {
        DependencyType.DEFAULT: [
            Depends(get_session),
            Depends(validate_organization_header),
        ],
        DependencyType.AUTH: [
            Depends(get_session),
            Depends(validate_organization_header),
        ],
    },
    RouterName.AGENT: {
        DependencyType.DEFAULT: [
            Depends(get_session),
            Depends(validate_organization_header),
        ],
        DependencyType.AUTH: [
            Depends(get_session),
            Depends(validate_authorization),
            Depends(validate_organization_header),
        ],
    },
    RouterName.SNAPSHOT: {
        DependencyType.DEFAULT: [
            Depends(get_session),
            Depends(validate_user_header),
            Depends(validate_organization_header),
        ],
        DependencyType.AUTH: [
            Depends(get_session),
            Depends(validate_authorization),
            Depends(validate_organization_header),
        ],
    },
    RouterName.MODEL: {
        DependencyType.DEFAULT: [
            Depends(get_session),
            Depends(validate_organization_header),
        ],
        DependencyType.AUTH: [
            Depends(get_session),
            Depends(validate_authorization),
            Depends(validate_organization_header),
        ],
    },
    RouterName.SCIM: {
        DependencyType.DEFAULT: [
            Depends(get_session),
            Depends(ScimAuthValidation()),
        ],
        DependencyType.AUTH: [
            Depends(ScimAuthValidation()),
        ],
    },
}
