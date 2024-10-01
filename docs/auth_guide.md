# Authentication

Prior to setting up any authentication, you will need to set up the base project using the `make first-run` command. If you've already done so, and both `configuration.yaml` and `secrets.yaml` files have been generated, you can skip ahead. 

## Adding Auth strategies

By default, Toolkit does not enforce any authentication strategies. These can be enabled in your `configuration.yaml` by using the `auth.enabled_auth` list parameter and adding `basic`, `google_oauth` or `oidc`.

For example:

```bash
auth:
    enabled_auth:
        - basic
        - google_oauth
        - oidc
```

Will enabled all 3 auth strategies. A `secret_key` must then be added to the `secrets.yaml` file for generating secure JWT tokens.

To generate an appropriate production `auth.secret_key` value, you can use the following python code:

```python
import secrets
print(secrets.token_hex(32))
```

Individual strategies might still require additional configuration, see below for more details.

## Available strategies

- BasicAuthentication: for email and password auth, no setup required.

- GoogleOAuth: for authentication with a Gmail account.
    - Requires a GCP project.
    - Requires setting up [Google OAuth 2.0](https://support.google.com/cloud/answer/6158849?hl=en).
    - In your `secrets.yaml` file, update the `auth.google_oauth.client_id` and `auth.google_oauth.client_secret` variables.
    
- OpenIDConnect: generic auth class for OpenIDConnectOAuth providers.
    - Requires an OIDC app for your provider (Google, Microsoft, Amazon, etc.)
    - In your `secrets.yaml` file, update the `auth.oidc.client_id`, `auth.oidc.client_secret`, and `auth.oidc.well_known_endpoint` variables.

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


## Configuring SCIM
**Notes**: 
* Currently, we only support OKTA for SCIM. We will add more providers as requested in the future.
* This only works if you already set up SSO via OIDC beforehand. We do not support password syncing.

SCIM allows you organization to synchronize your users and groups from your identity provider to the Toolkit. This has the benefit of:
* Automatically creating / deactivating users in the Toolkit when they are created / deactivated in your identity provider.
* Automatically assigning users to groups in the Toolkit when they are assigned to groups in your identity provider for access management.

### Create a username and password for SCIM
1. Fill in the following values in your configuration: SCIM_USER, SCIM_PASSWORD. Make sure to generate a secure secret for SCIM_PASSWORD

### Create a new SCIM application in OKTA.
1. Login to Okta as an Admin
2. From the Left nav goto: Applications->Applications
3. From the Applications screen, click “Browse App Catalog”:
4. Search for the application: SCIM 2.0 Test App (Basic Auth)
5. Click "Add Integration"
6. For "Application Label" enter a name for the application (e.g: Cohere Toolkit)
7. On the next screen leave the default configuration and click "Done"

### Configure the SCIM application in OKTA
1. Navigate to the tab "Provisioning"
2. Click "Configure API Integration"
3. Activate "Enable API integration"
4. Enter the following values:
   * SCIM 2.0 Base Url: `https://your-domain/scim/v2`
   * Username: Set this to the value of SCIM_USER
   * Password: Set this to the value of SCIM_PASSWORD
5. Click "Test API Credentials" to verify the credentials
6. Click "Save"
7. Select "To App" on the left side
8. Activate the following fields:
    * Create Users
    * Update User Attributes
    * Deactivate Users

### Assign Users
In this step you will synchronize selected users. Note that while we can select groups here, it will only sync users
in those groups, not the groups itself. This needs to be done in the next step.
1. Navigate to the "Assignments" tab
2. Click either "Assign to People" or "Assign to Groups"
3. Click "Save and Go Back"

### Synchronize Groups
This is optional but if groups should be synchronized, it needs to be configured like this:
1. Navigate to "Push Groups"
2. Click "Push Groups"
3. Select "Find Groups by name"
4. Enter the group you would like to push
5. Select the group
6. Click "Save"

