#!/bin/bash
set -e
# Backend App
copilot app init toolkit-app
copilot env init -n dev --profile default --default-config
copilot svc init --name toolkit-app-db --svc-type "Backend Service" --dockerfile ./aws_copilot_deploy/aws-db.Dockerfile --port 5432
copilot svc init --name toolkit-app-terrarium --svc-type "Backend Service" --dockerfile ./aws_copilot_deploy/aws-terrarium.Dockerfile --port 8080
copilot svc init --name toolkit-app-api --svc-type "Backend Service" --dockerfile ./aws_copilot_deploy/aws-api.Dockerfile --port 8000
copilot svc init --name toolkit-app-fe --svc-type "Backend Service" --dockerfile ./aws_copilot_deploy/aws-fe.Dockerfile --port 4000
copilot svc init --name toolkit-app-nginx --svc-type "Load Balanced Web Service" --dockerfile ./aws_copilot_deploy/aws-nginx.Dockerfile --port 8090

copilot env deploy --name dev
copilot svc deploy --name toolkit-app-db --env dev
copilot svc deploy --name toolkit-app-terrarium --env dev
copilot svc deploy --name toolkit-app-api --env dev
copilot svc exec -a toolkit-app -e dev --name toolkit-app-api --command "alembic -c src/backend/alembic.ini upgrade head"
copilot svc deploy --name toolkit-app-fe --env dev
copilot svc deploy --name toolkit-app-nginx --env dev
