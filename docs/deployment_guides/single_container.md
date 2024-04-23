# Single Container Setup Guide

This guide will show you how to build and start Cohere's Toolkit using a single container setup.
This single container can be deployed to your cloud platform, if needed.

Note: Azure Container instance and Cloud Run are stateless, so you will lose all your PostgreSQL data each restart.

## Cloud Deployment

You can deploy Toolkit with one click in Microsoft Azure Platform:
                                                                                         
[<img src="https://aka.ms/deploytoazurebutton" height="30px">](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fcohere-ai%2Ftoolkit%2Fmain%2Fazuredeploy.json)

### AWS ECS(Fargate) Deployment guide
- [AWS ECS Deployment](aws_ecs_single_container.md): Deploy the Toolkit single container to AWS ECS(Fargate).

## Build and Start

### Option 1 - Build from source

To build the toolkit in a single container locally, you can run the following command:
```bash
docker build -t cohere-ai/toolkit . -f standalone.Dockerfile   
```

You can then run the container with the following command:
```bash
docker run --name=cohere-toolkit -itd -e COHERE_API_KEY='Your Cohere API key here' -p 8000:8000 -p 4000:4000 cohere-ai/toolkit
```

### Option 2 - Pull from Registry

You can also pull a prebuilt image from the `cohere-ai` registry with:
```bash
docker pull ghcr.io/cohere-ai/cohere-toolkit:latest
```

Then run the containers with:

```bash
docker run --name=cohere-toolkit -itd -e COHERE_API_KEY='Your Cohere API key here' -p 8000:8000 -p 4000:4000 ghcr.io/cohere-ai/cohere-toolkit
```

```bash
docker run --name=cohere-toolkit -itd -e COHERE_API_KEY='Your Cohere API key here' -p 8000:8000 -p 4000:4000 ghcr.io/cohere-ai/cohere-toolkit
```

After either option, you can access the APIs at `http://localhost:8000/docs` to see the comprehensive list of endpoints, and the frontend Toolkit app at `http://localhost:4000`.


To stop the container, run:
```bash
docker stop cohere-toolkit
```

To start the container again, run:
```bash
docker start cohere-toolkit
```

### Enabling Python Interpreter
To enable the Python Interpreter tool, follow these steps:

Pull the latest Terrarium image
```bash
docker pull ghcr.io/cohere-ai/terrarium:latest
```

Then run the container with:

```bash
docker run --name=terrarium --hostname=terrarium -itd -p 8080:8080 ghcr.io/cohere-ai/terrarium
```

Then make sure your `.env` file contains `PYTHON_INTERPRETER_URL`, the default value should be `http://terrarium:8080`.