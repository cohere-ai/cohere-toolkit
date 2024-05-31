# Google Cloud Platform One Click Deployment Guide

Before deploying to Google Cloud Run, you'll need a postgres database accessible to your Google Cloud Project, authenticated by a username and password. You'll be prompted for a `DATABASE_URL` before the container builds.

[![Run on Google Cloud](https://deploy.cloud.run/button.svg)](https://deploy.cloud.run?dir=/)

## Deployment Steps

After clicking the button above, you'll be taken to the Google Cloud Console. Follow these steps to deploy the Toolkit:
- **Select a Project**: Choose the Google Cloud Project you want to deploy the Toolkit to. If you don't have a project, you need to create [one](https://cloud.google.com/resource-manager/docs/creating-managing-projects). 
- **Set the Region**: Choose the region you want to deploy the Toolkit to.
- **Set the DATABASE_URL environment variable**: Enter the connection string of the format `postgresql+psycopg2://USERNAME:PASSWORD@HOST:PORT/DB_NAME`. The `HOST` value here is the Public IP address of your provisioned PostgreSQL database, and the default `PORT` is 5432. Make sure to use the username and password pair you set when creating your SQL instance. For example, `postgresql+psycopg2://myuser:mypassword@<your-db-public-ip-address>:5432/toolkit`.
- **Set the Cohere API Key**: Enter your Cohere API key, you can create one on the [Cohere Dashboard](https://dashboard.cohere.com).
- **Allow access to the git registries**: Click 'yes' to allow access to the git registries.

## Post-Deployment Steps

After the deployment process is complete, you'll be able to access the Toolkit by navigating to the URL provided in the Google Cloud Shell.
Optionally you can get this URL using GCP console, to do it follow these steps:
- Click on the "Cloud Run" button on the left side of the screen
- Click on the toolkit-deploy service
- Click on the "URL" link to open the Toolkit in a new tab

## Possible Deployment Errors

If the deployment is stuck on pushing the image to the Container Registry close the shell and try to redeploy the service.

If the deployment is stuck in a pending state or the connection to your Google Cloud Shell was lost like shown below:
![](/docs/assets/cloud_shell_stuck.png)

or you get the nginx 502 error when trying to access the Toolkit URL,
it means that the deployment process was not completed successfully, and we need to create a new revision for our deployment with correct settings.

Cloud Run does not set the startupProbe settings to the correct value, so we need to set it in the new revision.

To do it follow next steps:
- Navigate to the Google Cloud Console
- Click on the "Cloud Run" button on the left side of the screen
- Click on the toolkit-deploy service
- Click on the "Edit & Deploy New Revision" button
- Scroll down to the "Health checks" section
- Delete the existing health check
- Click on the "Add health check" button
  - Select health check type: Startup check 
  - Select probe type: HTTP
  - Path (e.g./ready): /api/health
  - Port: 4000
  - Initial delay: 0
  - Period: 1 
  - Failure threshold: 120
  - Timeout: 1
  - Click "Add" button
- Click "Deploy" button

