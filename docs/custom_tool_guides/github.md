# Github Tool Setup

To set up the Github tool you will need a Github application. Follow the steps below to set it up:

## 1. Create a Github App

Head to the [Github Settings](https://github.com/settings/apps) and create a new app.
Specify App [permissions](https://docs.github.com/rest/overview/permissions-required-for-github-apps), Callback URL (for local setup - http://localhost:8000/v1/tool/auth).
Uncheck the `Webhook->Active` option. After creating the app, you will see the `General` section. Copy the `Client ID`, generate and copy `Client Secret` values.
That will be used for the environment variables specified below.
This tool also support OAuth Apps. See the [documentation](https://docs.github.com/en/apps/oauth-apps) for more information.

## 2. Set Up Environment Variables
Set the configuration in the `configuration.yaml`
```yaml
github:
    default_repos: 
      - repo1
      - repo2
    user_scopes: 
      - public_repo
      - read:org
```

Then set the following secrets variables. You can either set the below values in your `secrets.yaml` file:
```yaml
github:
    client_id: <your_client_id from step 1>
    client_secret: <your_client_secret from step 1>
```
or update your `.env` configuration to contain:
```dotenv
GITHUB_CLIENT_ID=<your_client_id from step 1>
GITHUB_CLIENT_SECRET=<your_client_secret from step 1>
GITHUB_DEFAULT_REPOS=["repo1","repo2"]
GITHUB_USER_SCOPES=["public_repo","read:org"]
```
Please note if the default repos are not set, the tool will process over all user repos.

## 3. Run the Backend and Frontend

run next command to start the backend and frontend:

```bash
make dev
```

## 4. Troubleshooting

If you encounter any issues with OAuth, please check the following [link](https://api.Github.com/authentication/oauth-v2#errors)
