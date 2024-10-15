# Google Cloud Text-to-Speech Setup

To use Google Cloud Text-to-Speech, you'll need to create a Google Cloud project and follow the steps below:

## 1. Enable Required APIs

Open the **Google Cloud Console**, navigate to **APIs & Services**, and enable:
- **Cloud Text-to-Speech API**
- **Cloud Translation API**

## 2. Create API Credentials

In the **Google Cloud Console**, go to **APIs & Services** > **Credentials**.
Click **Create Credentials** and select **API key**.
Copy the generated API key for using in the next step.

## 3. Configure Environment Variable

You can either set the API key in your `.env` file:

```bash
GOOGLE_CLOUD_API_KEY=<your_api_key>
```

or update your `secrets.yaml` configuration to contain:

```bash
google_cloud:
  api_key:<your_api_key>
```