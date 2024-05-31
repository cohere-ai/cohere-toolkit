# Authentication

## Adding Auth strategies

By default, the Toolkit does not enforce any authentication strategies, but they can be enabled from `src/backend/config/auth.py`.

The list of implemented authentication strategies exist in `src/backend/services/auth`. Currently, there exists:
- BasicAuthentication (for email/password auth): no setup required.
- GoogleOAuth: requires setting up [Google OAuth 2.0](https://support.google.com/cloud/answer/6158849?hl=en). You will need to retrieve a client ID and client secret and set them as environment variables.

To enable one or more of these strategies, simply add them to the `ENABLED_AUTH_STRATEGIES` list in the configurations.
