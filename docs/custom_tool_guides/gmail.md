# Gmail Tool Setup

To set up the Gmail tool you will need to configure API access in Google Cloud Console.

Follow the steps below to set it up:

## 1. Create Project in Google Cloud Console 

Head to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project.
After creating the app, you will see the `APIs & Services` section. Under `Enabled APIs & services`, enable the
Gmail API.

## 2. Configure OAuth Consent Screen

Before you can generate the API credentials, you must first configure the OAuth consent screen.

You will need to configure the `Application home page` and `Authorized domain 1` fields, with a URL and domain that
point to where you are running the Toolkit. If you are running it in a local environment, Ngrok can be used as a proxy
to access the to the Toolkit in local. Using `localhost` is not accepted value for these fields.

If you choose to use Ngrok, you can start it with:

`ngrok http -domain <your_custom_domain>.ngrok.dev 8000`

And then use the domain you used here in the OAuth Consent Screen configuration.

## 3. Generate Credentials

Once the OAuth consent screen has been configured, choose the `Credentials` menu option. Click `+ CREATE CREDENTIALS`
at the top, and choose the OAuth client ID option.

If running the Toolkit in your local environment, you can use `http://localhost` as the Authorized Javascript origin.

For the Authorized redirect URI, it must point to the Toolkit backend. The path should be `/v1/tool/auth`. For example:

```bash
    https://<your_backend_url>/v1/tool/auth
```

## 3. Set Up Environment Variables

Then set the following environment variables. You can either set the values in your `secrets.yaml` file:
```bash
Gmail:
    client_id: <your_client_id from the previous step>
    client_secret: <your_client_secret from the previous step>
```
or update your `.env` configuration to contain:
```bash
GMAIL_CLIENT_ID=<your_client_id from the previous step>
GMAIL_CLIENT_SECRET=<your_client_secret from the previous step>
```

## 4. Enable the Gmail Tool in the Frontend

To enable the Gmail tool in the frontend, you will need to modify the `src/interfaces/assistants_web/src/constants/tools.ts`
file. Add the `TOOL_GMAIL_ID` to the `AGENT_SETTINGS_TOOLS` list.

```typescript
export const AGENT_SETTINGS_TOOLS = [
  TOOL_HYBRID_WEB_SEARCH_ID,
  TOOL_PYTHON_INTERPRETER_ID,
  TOOL_WEB_SCRAPE_ID,
  TOOL_GMAIL_ID,
];
```

To enable the Gmail tool in the frontend for the base agent, you will need to modify the
`src/interfaces/assistants_web/src/constants/tools.ts` file. Remove `TOOL_GMAIL_ID` from the
`BASE_AGENT_EXCLUDED_TOOLS` list. By default, the Gmail Tool is disabled for the Base Agent.

```typescript
export const BASE_AGENT_EXCLUDED_TOOLS = [];
```

## 5. Run the Backend and Frontend

run next command to start the backend and frontend:

```bash
make dev
```
