from backend.services.auth import (
    BasicAuthentication
)

ENABLED_AUTH_STRATEGIES = [
    BasicAuthentication,
]