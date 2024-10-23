# AWS Deployment using AWS Copilot for Cohere's Toolkit

This guide provides instructions for deploying Cohere's Toolkit on AWS using AWS Copilot. AWS Copilot is a CLI tool that simplifies building, releasing, and managing production-ready applications on Amazon ECS with AWS Fargate.

## Limitations

- AWS Copilot does **not** support deployment using AWS root accounts. You must create an IAM user with the `AdministratorAccess` policy enabled.

## Prerequisites

Before starting, ensure you have:

- **An AWS account**
- **AWS CLI** installed and configured:
  - [Install AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
  - Run `aws configure` to set up your `AWS Access Key ID`, `Secret Access Key`, `region`, and `output format`
- **Docker** installed:
  - [Install Docker](https://docs.docker.com/get-docker/)
- **AWS Copilot** installed:
  - [Install AWS Copilot](https://aws.github.io/copilot-cli/)
- **Cohere's Toolkit repository** cloned
- **Environment Variables** set up in `.env`, `configuration.yaml`, and `secrets.yaml`:
  - Follow the [setup guide](/docs/setup.md) for configuration details

## Deployment Steps

### 1. Create an IAM User

1. Go to the [IAM console](https://console.aws.amazon.com/iam/home) and click **Users**.
2. Click **Create user** and enter a username.
3. Select **Provide user access to the AWS Management Console - optional** and choose password settings.
4. Click **Next: Permissions**, then **Attach policies directly**.
5. Search for `AdministratorAccess`, select it, and proceed with **Next**.
6. Review and click **Create user**.
7. After creating the user, select it and go to the **Security credentials** tab.
8. Click **Create access key**, choose `Other`, and proceed.
9. Copy the `Access key` and `Secret access key` and store them securely.

### 2. Configure the AWS CLI

- Run `aws configure` and input the `Access key`, `Secret access key`, `region`, and `output format`.

### 3. Set environment variables

The deployment script uses configuration values from either the .env or configuration.yaml file. 
Set the following environment variable in the .env file:
```
DATABASE_URL='postgresql+psycopg2://postgres:postgres@{service name}.{env name}.{app name}.local:5432'
```
Or, in the configuration.yaml file::
```yaml
database:
  url: postgresql+psycopg2://postgres:postgres@{service name}.{env name}.{app name}.local:5432
```
For the current deployment, the database URL should be:
```
postgresql+psycopg2://postgres:postgres@toolkit-app-db.dev.toolkit-app.local:5432
```
### 4. Deploy the Toolkit

1. Navigate to the root directory of the cloned repository.
2. Run the deployment script:
   ```bash
   ./aws_copilot_deploy/aws_deploy.sh
   ```
3. Wait for the deployment to complete. The script will output the URL of the deployed application.

### 5. Clean Up

- To delete the deployed application, run:
   ```bash
   ./aws_copilot_deploy/aws_cleanup.sh
   ```

## Detailed Description

The provided deployment script uses AWS Copilot to set up an application, environment, and services on AWS Fargate. This deployment includes:

- **Reverse Proxy**: Uses Nginx to route traffic between services, as AWS Copilot supports only one load-balanced service per application.
- **Containerized Database**: Uses a containerized database by default. You can modify the script to use Amazon RDS by following [these instructions](https://aws.github.io/copilot-cli/docs/developing/storage/) for setting up an RDS Aurora Serverless v2 cluster using `copilot storage init`.
- **Resource Allocation**: Adjust service resource settings (e.g., `cpu`, `memory`) in each service's `manifest.yml` file as needed.
- **Customizing Services**: Comment out unnecessary services in `aws_deploy.sh` or delete a service with:
   ```bash
   copilot svc delete
   ```
   Refer to the full [AWS Copilot documentation](https://aws.github.io/copilot-cli/docs/overview/) for more commands.