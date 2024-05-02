from backend.services.auth.basic import BasicAuthentication

__all__ = [
    "BasicAuthentication",
]

AUTH_STRATEGY_MAPPING = {
    "basic": BasicAuthentication,
}
