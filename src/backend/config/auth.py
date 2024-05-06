from backend.services.auth import BasicAuthentication

# Modify this to enable auth strategies.
ENABLED_AUTH_STRATEGIES = []

# Define the mapping from Auth strategy name to class obj.
# Does not need to be manually modified.
# Ex: {"Basic": BasicAuthentication}
ENABLED_AUTH_STRATEGY_MAPPING = {cls.NAME: cls for cls in ENABLED_AUTH_STRATEGIES}
