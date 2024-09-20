# Google Drive Tool Setup

To set up the Google Drive tool you will need a Google Cloud project, then follow the steps below:

## 1. Enable APIs

You'll need to head to GCP, navigate to APIs & Services and enable:
- Google Drive API
- Google Picker API

## 2. Set up your GCP credentials

In the Google Cloud Console, go to APIs & Services > Credentials.
Click Create Credentials and select OAuth 2.0 Client IDs.
Configure the OAuth consent screen if you haven't already.
Create OAuth 2.0 Client IDs for a Web application, specifying the necessary authorized redirect URIs.
Save the Client ID and Client Secret values and use them for the environment variables specified above.
## 3. Set Up Environment Variables

Then set the following environment variables. You can either set the below values in your `.env` file:

```bash
GOOGLE_DRIVE_CLIENT_ID=<your_client_id>
GOOGLE_DRIVE_CLIENT_SECRET=<your_client_secret>
NEXT_PUBLIC_GOOGLE_DRIVE_CLIENT_ID=${GOOGLE_DRIVE_CLIENT_ID}
NEXT_PUBLIC_GOOGLE_DRIVE_DEVELOPER_KEY=<your_developer_key>
```

or update your `secrets.yaml` configuration to contain:

```bash
google_drive:
    client_id:
    client_secret:
    developer_key:
```