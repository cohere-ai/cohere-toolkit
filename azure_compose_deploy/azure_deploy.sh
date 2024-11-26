#!/bin/bash
set -e
LOCATION=canadaeast
RESOURCE_GROUP=toolkitResourceGroup
APP_NAME=toolkit-app
APP_INSTANCE_SKU=P1V3
APP_PLAN_NAME=toolkit-app-plan
REGISTRY_NAME=toolkitregistry
REGISTRY_SKU=Basic
DB_SERVER_NAME=toolkitpostgre
DB_ADMIN_USER=postgres
DB_ADMIN_PASSWORD=postgres
DB_SKU_NAME=Standard_B1ms
DB_TIER=Burstable
DB_STORAGE_SIZE=32

# Login to Azure
az login
# Create Resource Group
az group create --name $RESOURCE_GROUP --location $LOCATION
# Create Registry for Docker images
az acr create --resource-group $RESOURCE_GROUP --name $REGISTRY_NAME --sku $REGISTRY_SKU
az acr update -n $REGISTRY_NAME --admin-enabled true
#Login to Registry
az acr login --name $REGISTRY_NAME
# Set PostgreSQL Server
az postgres flexible-server create --location $LOCATION --resource-group $RESOURCE_GROUP \
    --name $DB_SERVER_NAME --admin-user $DB_ADMIN_USER --admin-password $DB_ADMIN_PASSWORD \
    --sku-name $DB_SKU_NAME --tier $DB_TIER --storage-size $DB_STORAGE_SIZE \
    --public-access 0.0.0.0

# Build and push Docker images
docker buildx build --platform linux/amd64 -t $REGISTRY_NAME.azurecr.io/toolkit-app-api -f azure_compose_deploy/azure-api.Dockerfile .
docker push $REGISTRY_NAME.azurecr.io/toolkit-app-api
docker buildx build --platform linux/amd64 -t $REGISTRY_NAME.azurecr.io/toolkit-app-fe -f azure_compose_deploy/azure-fe.Dockerfile ./src/interfaces/assistants_web
docker push $REGISTRY_NAME.azurecr.io/toolkit-app-fe
docker buildx build --platform linux/amd64 -t $REGISTRY_NAME.azurecr.io/toolkit-app-nginx -f azure_compose_deploy/azure-nginx.Dockerfile .
docker push $REGISTRY_NAME.azurecr.io/toolkit-app-nginx
docker buildx build --platform linux/amd64 -t $REGISTRY_NAME.azurecr.io/toolkit-app-terrarium -f azure_compose_deploy/azure-terrarium.Dockerfile .
docker push $REGISTRY_NAME.azurecr.io/toolkit-app-terrarium

# Deploy Toolkit App
az appservice plan create --name $APP_PLAN_NAME --resource-group $RESOURCE_GROUP --sku $APP_INSTANCE_SKU --is-linux
az webapp create --resource-group $RESOURCE_GROUP --plan $APP_PLAN_NAME --name $APP_NAME \
  --multicontainer-config-type compose \
  --multicontainer-config-file azure_compose_deploy/docker-compose-azure.yml

az webapp config appsettings set  --name $APP_NAME --resource-group $RESOURCE_GROUP \
  --settings DBHOST="$DB_SERVER_NAME.postgres.database.azure.com" DBNAME="postgres" DBUSER="$DB_ADMIN_USER" \
   DBPASS="$DB_ADMIN_PASSWORD" DOCKER_REGISTRY_SERVER_URL="https://$REGISTRY_NAME.azurecr.io" DOCKER_REGISTRY_SERVER_USERNAME="$REGISTRY_NAME" \
    DOCKER_REGISTRY_SERVER_PASSWORD=$(az acr credential show -n $REGISTRY_NAME --query "passwords[0].value" -o tsv)
