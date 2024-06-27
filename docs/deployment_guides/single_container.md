# Single Container Setup Guide

This guide will show you how to build and start Cohere's Toolkit using a single container setup.
This single container can be deployed to your cloud platform, if needed.

Note: Azure Container instance and Cloud Run are stateless, so you will lose all your PostgreSQL data each restart.

## Cloud Deployment

You can deploy Toolkit with one click in Microsoft Azure Platform:

[<img src="https://aka.ms/deploytoazurebutton" height="30px">](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fcohere-ai%2Fcohere-toolkit%2Fmain%2Fazuredeploy.json)

This deployment type uses Azure Container Instances to host the Toolkit.
After your deployment is complete click "Go to resource" button.
1) Check the logs to see if the container is running successfully:
   - click on the "Containers" button on the left side of the screen
   - click on the container name
   - click on "Logs" tab to see the logs
2) Navigate to the "Overview" tab to see the FQDN of the container instance
3) Open the \<FQDN\>:4000 in your browser to access the Toolkit

### AWS ECS Deployment guides
- [AWS ECS Fargate Deployment](aws_ecs_single_container.md): Deploy the Toolkit single container to AWS ECS(Fargate).
- [AWS ECS EC2 Deployment](docs/deployment_guides/aws_ecs_single_container_ec2.md): Deploy the Toolkit single container to AWS ECS(EC2).

## Build and Start

### Option 1 - Build from source

To build the toolkit in a single container locally, you can run the following command:
```bash
docker build -t cohere-ai/toolkit . -f standalone.Dockerfile   
```

You can then run the container with the following command:
```bash
docker run --name=cohere-toolkit -itd -e COHERE_API_KEY='Your Cohere API key here' -p 8000:8000 -p 4000:4000 cohere-ai/cohere-toolkit
```
If you need to use community features, you can run the container with the following command:
```bash
docker run --name=cohere-toolkit -itd -e INSTALL_COMMUNITY_DEPS='true' -e COHERE_API_KEY='Your Cohere API key here' -p 8000:8000 -p 4000:4000 cohere-ai/cohere-toolkit
```

If you would like to use .env file to pass the parameters, you can mount it to the container using the following command.
If you need to use community features, please set `INSTALL_COMMUNITY_DEPS=true` in your .env file.
```bash
docker run --name=cohere-toolkit -itd --env-file .env -p 8000:8000 -p 4000:4000 cohere-ai/cohere-toolkit
```

### Option 2 - Pull from Registry

You can also pull a prebuilt image from the `cohere-ai` registry with:
```bash
docker pull ghcr.io/cohere-ai/cohere-toolkit:latest
```

Then run the container with:
```bash
docker run --name=cohere-toolkit -itd -e COHERE_API_KEY='Your Cohere API key here' -p 8000:8000 -p 4000:4000 ghcr.io/cohere-ai/cohere-toolkit
```

If you would like to use .env file to pass the parameters, you can mount it to the container using:
```bash
docker run --name=cohere-toolkit -itd --env-file .env -p 8000:8000 -p 4000:4000 ghcr.io/cohere-ai/cohere-toolkit
```

Please note that after running the container, you will need to wait some time for the all the services to start up. You can check the logs with:
```bash
docker logs cohere-toolkit
```
or you can check the status of the container with Docker desktop.

After either option, you can access the APIs at `http://localhost:8000/docs` to see the comprehensive list of endpoints, and the frontend Toolkit app at `http://localhost:4000`.


To stop the container, run:
```bash
docker stop cohere-toolkit
```

To start the container again, run:
```bash
docker start cohere-toolkit
```
