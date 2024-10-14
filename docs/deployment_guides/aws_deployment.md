# AWS deployment using AWS Copilot for Cohere's Toolkit

This guide will show you how to deploy Cohere's Toolkit on AWS using AWS Copilot. 
AWS Copilot is a command-line interface that makes it easy to build, 
release, and operate production-ready applications on Amazon ECS and AWS Fargate.

## Limitations

AWS Copilot doesn't work with aws root accounts, so you will need to create an IAM user with the AdministratorAccess policy enabled.

## Prerequisites
To follow this guide, you will need the following:
- An AWS account
- The AWS CLI installed and configured
  - To install the AWS CLI, follow the instructions [here](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
  - To configure the AWS CLI, run `aws configure` and enter your AWS Access Key ID, Secret Access Key, region, and output format
- Docker installed
  - To install Docker, follow the instructions [here](https://docs.docker.com/get-docker/) 
- AWS Copilot installed
  - To install AWS Copilot, follow the instructions [here](https://aws.github.io/copilot-cli/) 
- Cohere's Toolkit repository cloned
- Initial setup of the env variables in the `.env` file or in the `configuration.yaml` and `secrets.yaml` files
  - To set up the Toolkit, follow the instructions [here](/docs/setup.md)

## Steps

1. **Create an IAM user**
   - Go to the [IAM console](https://console.aws.amazon.com/iam/home) and click on `Users` in the left sidebar
   - Click on `Create user`
   - Enter a username and check `Provide user access to the AWS Management Console - optional`
   - Choose the password settings and click on `Next: Permissions`
   - Click on `Attach policies directly`
   - Search for `AdministratorAccess` and select it
   - Click on `Next` and set the tags if needed
   - Click on `Create user`
   - After that select the user in the list and click on `Security credentials` tab
   - Click on `Create access key`
   - Choose use case `Other` and click on `Next`
   - Add tags if needed and click on `Create access key`
   - Copy the `Access key` and `Secret access key` and save them in a secure location
2. **Configure the AWS CLI**
   - Run `aws configure` and enter the `Access key`, `Secret access key`, region, and output format

3. **Deploy the Toolkit**
   - Go to the pulled repository root directory
   - Run `./aws_copilot_deploy/aws_deploy.sh`
   - Wait for the deployment to finish
   - After the deployment is finished, you will see the URL of the deployed application
4. **Cleanup**
   - To delete the deployed application, run `./aws_copilot_deploy/aws_cleanup.sh`

## Detailed description
We have created a script that will deploy the Toolkit to AWS using AWS Copilot.
The script will create a new application, environment, and services in AWS Fargate.
Please note that the AWS Copilot doesn't allow to deploy more than one service with Load Balancer at the same application.
So this deployment uses Nginx as a reverse proxy to route the traffic to the services.
Please note that the deployment script is using containerised DB services for the database.
You can change it and use RDS if needed.
Please read this [AWS Copilot documentation](https://aws.github.io/copilot-cli/docs/developing/storage/) how to set up 
RDS Aurora Serverless v2 cluster using copilot storage init
Also we set the minimal resources for the services, you can change it in the `manifest.yml` file for each service - 
take a look at the `cpu` and `memory` settings in the `manifest.yml` file. 
If some service is not needed you can comment it in the `aws_deploy.sh` script.
To delete some service you can run `copilot svc delete` command and choose the service you want to delete.
The full list of commands you can find [here](https://aws.github.io/copilot-cli/docs/overview/). 

