## Amazon Elastic Container Service (ECS) Deployment Guide

### Requirements
- **AWS Account**
- **Docker Installed**
- **Cohere API Key**
- **AWS CLI Installed and Configured**
- **VPC, Subnets, Security Groups**
- **EC2 Instance**
- **ECS Cluster**
- **ECS Task Definition**
- **ECS Service**

**Optional:**
- Route 53 Domain Name (for custom domain)
- ECR Registry (for deploying the image)

### Deployment Steps

#### 1. Prepare Docker Image
You can use the public Docker image or push it to your own Amazon ECR registry.

- **To use the public image:**
  ```bash
  docker run -e COHERE_API_KEY='>>YOUR_API_KEY<<' -p 8000:8000 -p 4000:4000 ghcr.io/cohere-ai/cohere-toolkit:latest
  ```

- **To build and push to ECR:**
  ```bash
  docker build -t cohere-ai/toolkit . -f standalone.Dockerfile
  docker tag cohere-ai/toolkit <Your ECR Registry URL>:latest
  
  # If using ARM processor
  docker buildx build --platform linux/amd64 -t cohere-ai/toolkit . -f standalone.Dockerfile
  docker tag cohere-ai/toolkit <Your ECR Registry URL>:latest

  # Push the image to ECR
  aws ecr get-login-password --region <Your AWS Region> | docker login --username AWS --password-stdin <Your ECR Registry URL>
  docker push <Your ECR Registry URL>:latest
  ```

#### 2. Create ECS Cluster
- Go to the ECS dashboard and create a new cluster:
  - **Cluster Name:** ToolkitCluster
  - **Infrastructure:** Amazon EC2 instances
  - **Auto Scaling Group:** Create new ASG
  - **Provisioning:** Choose On-Demand or Spot Instance
  - **EC2 Instance Type:** t3.xlarge
  - **Desired Capacity:** Minimum/Maximum: 1
  - **Network Settings:** Select your VPC, subnets, and create a security group with the following inbound rules:
    - Custom TCP Rule, Port Range: 8000 (Source: Anywhere IPv4)
    - Custom TCP Rule, Port Range: 4000 (Source: Anywhere IPv4)
  - **Auto-assign Public IP:** On

#### 3. Create ECS Task Definition
- Define a new task with the following settings:
  - **Task Definition Family:** ToolkitTask
  - **Launch Type:** Amazon EC2
  - **Network Mode:** Host
  - **Task CPU:** 3 vCPU
  - **Task Memory:** 12 GB
  - **Container Definitions:** Add a new container:
    - **Name:** ToolkitContainer
    - **Image:** `<Your ECR Registry URL>/toolkit:latest` or `ghcr.io/cohere-ai/cohere-toolkit:latest`
    - **Port Mappings:** TCP 8000:8000, 4000:4000
    - **Environment Variables:**
      - `COHERE_API_KEY=<Your Cohere API Key>`
      - `NEXT_PUBLIC_API_HOSTNAME='http://<Your EC2 Instance Public IPv4 DNS>:8000'`

#### 4. Create ECS Service
- Create a new service:
  - **Existing Cluster:** ToolkitCluster
  - **Task Definition:** ToolkitTask
  - **Service Name:** ToolkitService
  - **Desired Tasks:** 1
  - **Deployment Configuration:** Rolling update
  - Click **Create** to set up the service.

### Accessing the Toolkit
Once the service is running, access the Toolkit frontend at:
- **Frontend:** `http://<Your EC2 Instance Public IPv4 DNS>:4000`
- **API Documentation:** `http://<Your EC2 Instance Public IPv4 DNS>:8000/docs`

### Notes
- This guide provides a sample deployment for demonstration purposes; it is not recommended for production use.
- You can deploy the frontend and API as separate services if needed.
