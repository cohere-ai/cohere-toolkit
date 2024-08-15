# Authentication

Prior to setting up any authentication, we recommend setting up the base project using the `make first-run` command. If you've already done so, you can skip ahead.

## Adding Auth strategies

By default, the Toolkit does not enforce any authentication strategies, but they can be enabled from `src/backend/config/auth.py`.

This is the current list of implemented Auth strategies:

- BasicAuthentication: for email and password auth, no setup required.

- GoogleOAuth: for authentication with a Gmail account.
    - Requires a GCP project.
    - Requires setting up [Google OAuth 2.0](https://support.google.com/cloud/answer/6158849?hl=en).
    - In your `secrets.yaml` file, update the `auth.google_oauth.client_id` and `auth.google_oauth.client_secret` variables.
- OpenIDConnect: generic auth class for OpenIDConnectOAuth providers.
    - Requires an OIDC app for your provider (Google, Microsoft, Amazon, etc.)
    - In your `secrets.yaml` file, update the `auth.oidc.client_id`, `auth.oidc.client_secret`, and `auth.oidc.well_known_endpoint` variables.

To enable one or more of these strategies, add them to the `ENABLED_AUTH_STRATEGIES` list in the `backend/config/auth.py` file, then add any required environment variables in your `secrets.yaml` file, then generate a secret key to be used as the `auth.secret_key` environment variable. This is used to encode and decode your access tokens for both login OAuth flows and Tool auth.

To generate an appropriate production `auth.secret_key` value, you can use the following python code:

```python
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

If your strategy requires environment variables, create a new `<AUTH_METHOD>Settings` class, you can refer to the `settings.py` file for more examples.

OAuth strategies should implement the `authorize` method to verify an authorization code and return an access token.
