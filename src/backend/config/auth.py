from backend.services.auth import BasicAuthentication, GoogleOAuth

# Modify this to enable auth strategies.
ENABLED_AUTH_STRATEGIES = []

# Define the mapping from Auth strategy name to class obj - does not need to be manually modified.
# During runtime, this will create an instance of each enabled strategy class.
# Ex: {"Basic": BasicAuthentication()}
ENABLED_AUTH_STRATEGY_MAPPING = {cls.NAME: cls() for cls in ENABLED_AUTH_STRATEGIES}
