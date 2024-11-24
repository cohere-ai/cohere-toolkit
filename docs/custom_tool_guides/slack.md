# Slack Tool Setup

To set up the Slack tool you will need a Slack application. Follow the steps below to set it up:

## 1. Create a Slack App

Head to the [Slack API](https://api.slack.com/apps) and create a new app.
After creating the app, you will see the `App Credentials` section. Copy the `Client ID` and `Client Secret` values.
That will be used for the environment variables specified above.

## 2. Set up OAuth & Permissions
OAuth flow is required to authenticate users with Slack. 
To enable it please set the following redirect URL to your app's settings:
```bash
    https://<your_backend_url>/v1/tool/auth
```
Please note that for the local development you will need to enable HTTPS. 
See the [Setup HTTPS for Local Development](#5-setup-https-for-local-development) section for more details.
If you are using a local https setup, redirect url should be 
```
 https://localhost:8000/v1/tool/auth
```
Also, you can set up a proxy, such as [ngrok](https://ngrok.com/docs/getting-started/), to expose your local server to the internet.

The Slack tool uses User Token Scopes to access the user's Slack workspace.
The required and the default permission scope is `search:read`.
Set it in the `OAuth & Permissions` section of your Slack app settings.

To work with the Slack Tool Advanced token security via token rotation is required.
To enable it, go to the `OAuth & Permissions` section of your Slack app settings and click 'Opt in' button in the 'Advanced token security via token rotation' section.

More information about the OAuth flow can be found [here](https://api.slack.com/authentication/oauth-v2).

## 3. Set Up Environment Variables

Then set the following environment variables. You can either set the below values in your `secrets.yaml` file:
```bash
slack:
    client_id: <your_client_id from step 1>
    client_secret: <your_client_secret from step 1>
```
or update your `.env` configuration to contain:
```bash
SLACK_CLIENT_ID=<your_client_id from step 1>
SLACK_CLIENT_SECRET=<your_client_secret from step 1>
```

## 4. Setup HTTPS for Local Development

To enable HTTPS for local development, the self-signed certificate needs to be generated.
Run the following command in the project root directory to generate the certificate and key:

```bash
 openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

Then, update the backend Docker configuration(src/backend/Dockerfile) to use the generated certificate.
Just change next lines in the Dockerfile:
```Dockerfile
COPY pyproject.toml poetry.lock cert.pem key.pem ./ 
```
and 
```Dockerfile
CMD uvicorn backend.main:app --reload --host 0.0.0.0 --port ${PORT} --timeout-keep-alive 300 --ssl-keyfile /workspace/key.pem --ssl-certfile /workspace/cert.pem
```
Change NEXT_PUBLIC_API_HOSTNAME environment variable in the .env `https` protocol:
```bash
NEXT_PUBLIC_API_HOSTNAME=https://localhost:8000
```

or in the configurations.yaml file:

```yaml
auth:
  backend_hostname: https://localhost:8000
```

To run the Frontend with HTTPS, update the `start` script in the `package.json` file:

```json
"scripts": {
    "dev": "next dev --port 4000 --experimental-https",
..........
}
```

Add the following line to the 'docker-compose.yml' file to the frontend environment variables:

```yaml
    NEXT_PUBLIC_API_HOSTNAME=https://localhost:8000
```

and change the API_HOSTNAME to

```yaml
    API_HOSTNAME: https://localhost:8000
```
also change the src/interfaces/assistants_web/.env.development file env variables to use https.

## 5. Run the Backend and Frontend

run next command to start the backend and frontend:

```bash
make dev
```

## 6. Troubleshooting

If you encounter any issues with OAuth, please check the following [link](https://api.slack.com/authentication/oauth-v2#errors)
For example, if you see the invalid_team_for_non_distributed_app error,
please ensure the app is distributed or try logging in with the workspace owner's account.