# Authentication

## Adding Auth strategies

By default, the Toolkit does not enforce any authentication strategies, but they can be enabled from `src/backend/config/auth.py`.

This is the current list of implemented Auth strategies:

- BasicAuthentication (for email/password auth): no setup required.
- GoogleOAuth: requires setting up [Google OAuth 2.0](https://support.google.com/cloud/answer/6158849?hl=en). To enable this strategy, you will need to configure your Google OAuth app and retrieve `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` values.
- OpenIDConnect: To enable this strategy, you will need to configure your SSO app and retrieve `OIDC_CLIENT_ID`, `OIDC_CLIENT_SECRET`, and `OIDC_WELL_KNOWN_ENDPOINT` values. Note that this should work with any OAuth app that follows OpenID Connect conventions, the strategy assumes that the well-known endpoint will return the required endpoints. See `oidc.py` for implementation details.

To enable one or more of these strategies, add them to the `ENABLED_AUTH_STRATEGIES` list in the `backend/config/auth.py` file, then add any required environment variables in your `.env` file, and generate a secret key to be used as the `AUTH_SECRET_KEY` environment variable. This is used to encode and decode your access tokens for both login OAuth flows and Tool auth.

Regarding the `AUTH_SECRET_KEY` variable, if you want to test auth any string will suffice.
For production use-cases, it is recommended to run the following python commands in a local CLI to generate a random key:

```
import secrets
print(secrets.token_hex(32))
```

## Configuring your OAuth app's Redirect URI

When configuring your OAuth apps, make sure to whitelist the Redirect URI to the frontend endpoint, it should look like 
`<FRONTEND_HOST>/auth/<STRATEGY_NAME>`. For example, your Redirect URI will be `http://localhost:4000/auth/google` if you're running the GoogleOAuth class locally.

## Enabling Proof of Key Code Exchange (PKCE)

Many OIDC-compliant auth providers also implement PKCE for added protection. This involves generating `code_verifier` and `code_challenge` values in the frontend and using these values to validate that the same entity that initially logged in with the auth provider is the one requesting an access token from an authorization code. 

For more [details click here.](https://oauth.net/2/pkce/)

To enable the additional PKCE auth flow, you will need to first ensure your auth provider is PKCE-compliant, then set the `PKCE_ENABLED` class attribute in your OIDCConnect auth strategy to `True`. 

## Implementing new Auth strategies

To implement a new strategy, refer to the `backend/services/auth/strategies` folder. Auth strategies will need to inherit from one of two base classes, `BaseAuthenticationStrategy` or `BaseOAuthStrategy`.

If your strategy requires environment variables, create a new `<AUTH_METHOD>Settings` class that inherits from `Settings`. The values you set in your Settings class will automatically be retrieved from the `.env` file.

OAuth strategies should implement the `authorize` method to verify an authorization code and return an access token.
