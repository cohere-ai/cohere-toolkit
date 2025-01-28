# Sharepoint Tool Setup

To setup the Sharepoint tool you need to configure API access via the following steps

## 1. Configure Tenant ID and Client ID

Your Microsoft Tenant ID and Client ID can be found my navigating to the [Micorsoft Entra Admin Center](https://entra.microsoft.com/) and then going to the `Overview` Page under the `Identity Section`. There the Tenant ID is listed as Tenant ID, and the Client ID is listed as the Application ID.

Copy your Tenant ID into the `configuration.yaml` file in the config directory of the backend, and your Client ID into the `secrets.yaml` file in the config directory of the backend.

## 2. Register New Application

Navigate to the `App registration` page under `Applications` on the same [Micorsoft Entra Admin Center](https://entra.microsoft.com/) website.

Click `New registration` to register a new application. Enter a name and select the proper account type. Single tenant is the norm unless you know of otherwise.

Under redirect URI select Web as the path should be `/v1/tool/auth`. For example:

```bash
    https://<your_backend_url>/v1/tool/auth
```

Click `Register` to Complete the Application Registration

## 3. Configure Permissions

Under the newly registered application navigate to the `API permissions` page. There you need to Click `Add a permission`, select `Microsoft Graph`, then `delegated permissions`. Next search `files.read.all` and check the box, then search `sites.read.all` and check the box. Then Click `Add permissions`.

## 3. Configure Client Secret

Under the newly registered application navigate to the `Certificates & secrets` page. Click `New client secret`, enter a description and an expiry then click `Add`. Your new Client Secret is only available to copy under the `value` column of the table right now. Copy it into the `secrets.yaml` file in the config directory of the backend.

## 5. Run the Backend and Frontend

run next command to start the backend and frontend:

```bash
make dev
```
