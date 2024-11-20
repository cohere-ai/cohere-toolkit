#!/bin/bash
set -e
RESOURCE_GROUP=toolkitResourceGroup

az group delete --name $RESOURCE_GROUP
