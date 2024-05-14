from backend.config.auth import ENABLED_AUTH_STRATEGY_MAPPING


def is_enabled_authentication_strategy(strategy_name: str) -> bool:
    # Check the strategy is valid and enabled
    if strategy_name not in ENABLED_AUTH_STRATEGY_MAPPING.keys():
        return False

    return True
