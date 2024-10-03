# Google Cloud Platform Deployment Guide

This guide will show you how to deploy Cohere's Toolkit on Google Cloud.

## Limitations

Note that this guide will not set up IAM policies for you on GCP. Both the `toolkit-backend` and `toolkit-frontend` containers are deployed with the `allow-unauthenticated` option to help you deploy an MVP faster. Additionally, the `CORSMiddleware` used in `src/backend/main.py` allows all origins by default. For better security, replace the wildcard with the frontend container after deploying it.

## Enabling Required APIs

To start, ensure you have all the required APIs enabled. The deployment will require the following APIs enabled:

- Cloud SQL Admin API
- Compute Engine API
- Cloud Build API
- Cloud Run Admin API
- Container Registry API
- Cloud Resource Manager API

## Granting Cloud Build Permissions

To deploy from Cloud Build to Cloud Run, you will need to grant the Cloud Run Admin and Service Account User roles to your Cloud Build service account. 

1. [Go to the Cloud Build settings page](https://console.cloud.google.com/cloud-build/settings).
2. In the `Service Account permissions` panel, set the status of the `Cloud Run Admin` role to *ENABLED*. 
3. In the additional steps pop-up, click *GRANT ACCESS TO ALL SERVICE ACCOUNTS*.

Your Cloud Build settings should now have Cloud Run and Service Accounts set to *ENABLED*.

## Provisioning Cloud SQL PostgreSQL Database

1. On the Google Console dashboard, search `Cloud SQL` in the top search bar, then select `Create Instance` > `Choose PostgreSQL`.
2. On the setup screen, set a Container ID (e.g., `toolkit-db`) and a password for the default `postgres` user.
3. Select the `PostgreSQL 14` database version.
4. Select a zone and availability, keeping the default values if needed.
5. Choose a preset to determine the memory and CPU allocated to your DB instance. For a simple testing database, you can select `Enterprise > Sandbox`, and modify this later if needed.
6. Select `Create Instance`, which should take a couple of minutes for your database to be set up.
7. Once finished, select your Database instance from the main Cloud SQL UI, then in the left-hand side panel, select `Databases` > `Create Database`, and create a new database (e.g., `toolkit`).
8. Head to `Connections` and select the `Networking` tab. Click `Add A Network` and add any name for it, along with the IP value of `0.0.0.0/0`.
9. Once everything is set up, note down the public connection IP to your database.

## Setting Up gcloud CLI and cloudbuild.yaml

1. [Install the gcloud CLI](https://cloud.google.com/sdk/docs/install).
2. Run the following command:

   ```bash
   gcloud auth login
   ```

   Authenticate and select the project you provisioned the PostgreSQL database in.

3. Open the `cloudbuild.yaml` file located in the root of this project. You will have several variables to fill in the `substitutions` section:

   - **_GCP_PROJECT_ID**: Your GCP project ID.
   - **_GCP_REGION**: The region you want to deploy to (e.g., `us-central1`).
   - **_DATABASE_URL**: A connection string in the format `postgresql://USERNAME:PASSWORD@HOST:PORT/DB_NAME`. The `HOST` value is the public IP address of your provisioned PostgreSQL database, and the default `PORT` is 5432. Use the username and password pair you set when creating your SQL instance. For example: `postgresql://myuser:mypassword@<your-db-public-ip-address>:5432/toolkit`.
   - **_COHERE_API_KEY**: Your Cohere API key, which you can create on the [Cohere Dashboard](https://dashboard.cohere.com).

4. Once completed, run the following command:

   ```bash
   gcloud builds submit --region=<YOUR_GCP_REGION>
   ```

This should build the Docker images, push them to the Container Registry, and finally deploy them to Cloud Run. If you encounter any issues, ensure the substitution variables are correctly set.

After deploying the Cloud Run containers, it is recommended to set the minimum number of containers to 1 for both the frontend and backend containers to avoid any cold starts.

You are now done setting up Cohere's Toolkit on Google Cloud!

## Limitations

Note that because Google Cloud Run containers are stateless and do not support Docker volumes, the file storage mechanism is not available for GCP deployments out of the box. Therefore, uploaded files to the Toolkit will be erased if your containers restart.

To get around this limitation, you will need to implement your own file storage system logic using Google Cloud Storage (or any other file storage system).