# Azure App Service Deployment

This guide provides instructions for deploying Cohere's Toolkit on Azure App Service using Docker Compose.

## Limitations

- **Azure App Service** supports multi-container apps only on Linux-based plans. This guide uses a Linux-based plan.
- **Azure multi-container apps** are in preview and may have limitations. 
Refer to the [Azure documentation](https://learn.microsoft.com/en-us/azure/app-service/configure-custom-container?tabs=debian&pivots=container-linux#configure-multi-container-apps) for the latest information.


## Prerequisites

Before starting, ensure you have:

- **An Azure admin account**
- **Active Azure subscription**
- **Azure CLI** installed:
  - [Install Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- **Docker** installed:
  - [Install Docker](https://docs.docker.com/get-docker/)
- **Cohere's Toolkit repository** [cloned](https://github.com/cohere-ai/cohere-toolkit/pulls)
- **Environment Variables** set up in `azure_compose_deploy/configuration.yaml`, and `azure_compose_deploy/secrets.yaml`:
  - Follow the [setup guide](/docs/setup.md) for configuration details

## Deployment Steps

### 1. Log in to Azure and set the subscription

### 2. Configure the setup script
Set the deployment script variables in the `azure_compose_deploy/azure_deploy.sh` file:

```dotenv
LOCATION=canadaeast # Azure region
RESOURCE_GROUP=toolkitResourceGroup # Resource group name
APP_NAME=toolkit-app # App name
APP_INSTANCE_SKU=P1V3 # App instance SKU
APP_PLAN_NAME=toolkit-app-plan # App plan name
REGISTRY_NAME=toolkitregistry # Docker Registry name
REGISTRY_SKU=Basic # Docker Registry SKU
DB_SERVER_NAME=toolkitpostgre # Database server name
DB_ADMIN_USER=postgres # Database admin user
DB_ADMIN_PASSWORD=postgres # Database admin password
DB_SKU_NAME=Standard_B1ms # Database SKU name
DB_TIER=Burstable # Database tier
DB_STORAGE_SIZE=32 # Database storage size
```


### 3. Set environment variables
- Database URL in `azure_compose_deploy/configuration.yaml`:
```yaml
database:
  url: postgresql+psycopg2://{db_user}:{db_user_password}@{db_server_name}.postgres.database.azure.com:5432
```
For the current deployment, the database URL should be:
```
postgresql+psycopg2://postgres:postgres@toolkitpostgre.postgres.database.azure.com:5432
```
If you have a different database URL, update the `database.url` in the `azure_compose_deploy/configuration.yaml` file.
Also remove the database related commands from the deployment script `azure_compose_deploy/azure_deploy.sh` file.

- Secrets in `azure_compose_deploy/secrets.yaml`:
```yaml
deployments:
  cohere_platform:
    api_key: "your_cohere_api_key"
```

### 4. Deploy the Toolkit

1. Navigate to the root directory of the cloned repository.
2. Run the deployment script:
   ```bash
   ./azure_compose_deploy/azure_deploy.sh
   ```
3. Loggin to Azure in the browser and grant access to the Azure CLI.
4. Chose the subscription to use in the console.
5. The script will deploy the Toolkit to Azure App Service.
6. Once the deployment is complete, wait for the services to start.
7. To check logs navigate to the Azure portal and see the logs for the toolkit-app service.

### 5. Clean Up

- To delete the deployed application and services, run the cleanup script:
   ```bash
   ./azure_compose_deploy/azure_cleanup.sh
   ```

## Detailed Description

The provided deployment script uses Azure cli to set up an Toolkit application, database and services on Azure. This deployment includes:
- **Toolkit Application**: Uses Azure App Service to host the Toolkit application.
- **Docker Registry**: Uses Azure Container Registry to store Docker images.
- **Database**: Uses [Azure PostgreSQL flexible server](https://docs.microsoft.com/en-us/azure/postgresql/flexible-server/overview) to store data.
- **Reverse Proxy**: Uses Nginx to route traffic between services.
- **Services**: Uses Azure App Service to host the Toolkit services(API and Frontend).
- **Python interpreter tool**: Terrarium uses Pyodide to run Python code in the browser. 
- **Environment Variables**: Set up in the `azure_compose_deploy/configuration.yaml` and `azure_compose_deploy/secrets.yaml` files.
- **Customizing Services**: To add some additional services, make Docker files and add them to the `azure_compose_deploy` directory. 
To include them in the deployment, modify the `azure_compose_deploy/docker-compose-azure.yml` file.
To add some additional Azure services, modify the `azure_compose_deploy/azure_deploy.sh` file to add it.
Detailed information about the az cli commands can be found in the [Azure CLI documentation](https://docs.microsoft.com/en-us/cli/azure/).

## Production Considerations
- **Scaling**: Azure App Service can scale automatically based on demand. App service supports horizontal and vertical scaling.
- **Monitoring**: Use Azure Monitor to monitor the Toolkit application.

