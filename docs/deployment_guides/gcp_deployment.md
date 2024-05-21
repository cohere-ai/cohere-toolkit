# Google Cloud Platform Deployment Guide

This guide will show you how to deploy Cohere's Toolkit on Google Cloud.

## Limitations

Note that this guide will not setup IAM policies for you on GCP, notably both the `toolkit-backend` and `toolkit-frontend` containers are deployed with the `allow-unauthenticated` option to help you deploy an MVP faster. In addition, the CORSMiddleware used in `src/backend/main.py` also allows all origins by default, for more security you should replace the wildcard with the frontend container after deploying it.

## Enabling Required APIs

To start, make sure you have all the required APIs [enabled.](https://console.cloud.google.com/apis/enableflow?apiid=sqladmin,compute.googleapis.com,cloudbuild.googleapis.com,run.googleapis.com,containerregistry.googleapis.com,cloudresourcemanager.googleapis.com&redirect=https:%2F%2Fcloud.google.com%2Fbuild%2Fdocs%2Fdeploying-builds%2Fdeploy-cloud-run&_ga=2.126548239.387354146.1710956350-717629198.1710450463&authuser=1&supportedpurview=project)

The deployment will require the following APIs enabled:
- Cloud SQL Admin API
- Compute Engine API
- Cloud Build API
- Cloud Run Admin API
- Container Registry API
- Cloud Resource Manager API

## Granting Cloud Build permissions

Next, to deploy from Cloud Build to Cloud Run you will need to grant the Cloud Run Admin and Service Account User roles to your Cloud Build service account.

[Go to the Cloud Build settings page](https://console.cloud.google.com/cloud-build/settings?_ga=2.180485797.387354146.1710956350-717629198.1710450463). Int the `Service Account permissions` panel, set the status of the `Cloud Run Admin` role to *ENABLED*. In the additional steps pop-up, click *GRANT ACCESS TO ALL SERVICE ACCOUNTS*.

Your Cloud Build settings should now have Cloud Run and Service Accounts set to *ENABLED*.

## Provisioning Cloud SQL PostgreSQL database

On the Google Console dashboard, search `Cloud SQL` in the top search bar, then select `Create Instance` > `Choose PostgreSQL`. This will open up a configuration page for your new PostgreSQL DB instance.

- On the setup screen, set a Container ID (e.g: `toolkit-db`), and a password for the default `postgres` user.
- Select the `PostgreSQL 14` database version.
- Select a zone and availability, keeping the default values if needed.
- You can choose a preset to determine the memory and CPU allocated to your DB instance. For a simple testing database, you can select `Enterprise > Sandbox`, you can modify this later if needed.

Now select `Create Instance`, it should take a couple of minutes for your database to be set up.

Once finished, select your Database instance from the main Cloud SQL UI, then in the left-hand side panel select `Databases` > `Create Database`, now create a new database (e.g: `toolkit`).

Now head to `Connections`, and select the `Networking` tab. Here you will click `Add A Network` and add any name for it, along with the IP value of `0.0.0.0/0`.

Once everything is setup, note down the public connection IP to your database.

## Setting up gcloud CLI and cloudbuild.yaml

We'll now prepare the backend and frontend images, and deploy them to Cloud Run. 
To get started, [install the gcloud CLI](https://cloud.google.com/sdk/docs/install).

You will then need to run:

```bash
gcloud auth login
```

Making sure that you authenticate and select the project you provisioned the PostgreSQL database in.

Now open the `cloudbuild.yaml` file located in the root of this project. You will have several variables to fill in the `substitutions` section.

- _GCP_PROJECT_ID: Your GCP project ID.
- _GCP_REGION: The region you want to deploy to, e.g: `us-central1`.
- _DATABASE_URL: A connection string of the format `postgresql://USERNAME:PASSWORD@HOST:PORT/DB_NAME`. The `HOST` value here is the Public IP address of your provisioned PostgreSQL database, and the default `PORT` is 5432. Make sure to use the username and password pair you set when creating your SQL instance. For example, `postgresql://myuser:mypassword@<your-db-public-ip-address>:5432/toolkit`.
- _COHERE_API_KEY: Your Cohere API key, you can create one on the [Cohere Dashboard](https://dashboard.cohere.com).

Once completed, run:

```bash
gcloud builds submit --region=<YOUR_GCP_REGION>
```

This should build the docker images, push them to the Container Registry, then finally deploy them to Cloud Run. If you're encountering any issues, make sure the substitution variables are correctly set.

After deploying the Cloud Run containers, it is recommended to set the minimum number of containers to 1 for both the frontend and backend containers to avoid any cold starts.

You are now done setting up Cohere's Toolkit on Google Cloud!

## Limitations

Note that because Google Cloud Run containers are stateless and do not support Docker volumes, the file storage mechanism is not available for GCP deployments out of the box, so *uploaded files to the Toolkit will be erased* if your containers restart.

To get by this limitation, you will have to implement your own file storage system logic using Google Cloud Storage (or any other file storage system). 
