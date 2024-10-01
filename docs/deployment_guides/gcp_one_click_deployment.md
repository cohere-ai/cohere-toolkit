# Google Cloud Platform One-Click Deployment Guide

Before deploying to Google Cloud Run, you'll need a PostgreSQL database accessible to your Google Cloud Project, authenticated by a username and password. You'll be prompted for a `DATABASE_URL` before the container builds.

[![Run on Google Cloud](https://deploy.cloud.run/button.svg)](https://deploy.cloud.run?dir=/)

## Deployment Steps

After clicking the button above, you'll be taken to the Google Cloud Console. Follow these steps to deploy the Toolkit:

1. **Select a Project**: Choose the Google Cloud Project you want to deploy the Toolkit to. If you don't have a project, you need to create [one](https://cloud.google.com/resource-manager/docs/creating-managing-projects).
   
2. **Set the Region**: Choose the region you want to deploy the Toolkit to.

3. **Set the `DATABASE_URL` Environment Variable**: Enter the connection string in the format:

   ```
   postgresql+psycopg2://USERNAME:PASSWORD@HOST:PORT/DB_NAME
   ```

   The `HOST` value here is the public IP address of your provisioned PostgreSQL database, and the default `PORT` is 5432. Use the username and password pair you set when creating your SQL instance. For example:

   ```
   postgresql+psycopg2://myuser:mypassword@<your-db-public-ip-address>:5432/toolkit
   ```

4. **Set the Cohere API Key**: Enter your Cohere API key, which you can create on the [Cohere Dashboard](https://dashboard.cohere.com).

5. **Allow Access to the Git Registries**: Click 'Yes' to allow access to the Git registries.

## Post-Deployment Steps

Once the deployment process is complete, you can access the Toolkit by navigating to the URL provided in the Google Cloud Shell. 

To retrieve this URL using the GCP console, follow these steps:

1. Click on the "Cloud Run" button on the left side of the screen.
2. Click on the `toolkit-deploy` service.
3. Click on the "URL" link to open the Toolkit in a new tab.

## Possible Deployment Errors

If the deployment is stuck on pushing the image to the Container Registry, close the shell and try to redeploy the service.

If the deployment is stuck in a pending state or you lose connection to your Google Cloud Shell (as shown below):

![Cloud Shell Stuck](path/to/your/image.png)

or you receive an nginx 502 error when trying to access the Toolkit URL, it indicates that the deployment process was not completed successfully. In this case, you'll need to create a new revision for your deployment with the correct settings.

### To Create a New Revision:

1. Navigate to the Google Cloud Console.
2. Click on the "Cloud Run" button on the left side of the screen.
3. Click on the `toolkit-deploy` service.
4. Click on the "Edit & Deploy New Revision" button.
5. Scroll down to the "Health checks" section.
6. Delete the existing health check.
7. Click on the "Add health check" button:
   - **Select health check type**: Startup check
   - **Select probe type**: HTTP
   - **Path (e.g., /ready)**: `/api/health`
   - **Port**: `4000`
   - **Initial delay**: `0`
   - **Period**: `1`
   - **Failure threshold**: `120`
   - **Timeout**: `1`
   - Click the "Add" button.
8. Click the "Deploy" button.

By following these steps, you should be able to resolve any deployment issues and successfully run the Toolkit on Google Cloud.