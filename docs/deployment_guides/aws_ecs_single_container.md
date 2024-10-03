## Amazon Elastic Container Service (ECS) Deployment

### Requirements:
- AWS account
- Docker installed
- Docker image of the Toolkit from the public registry
- Cohere API key
- AWS CLI installed and configured
- VPC
- Subnets
- Security groups
- Load balancer
- ECS Cluster
- ECS Task definition
- ECS Service

### Optional requirements:
- Route 53 domain name (for a custom domain name)
- ECR registry (to deploy the image to)

### Deployment Steps:

1. **Docker Image**  
   The Toolkit Docker image is available on the public registry at `ghcr.io/cohere-ai/cohere-toolkit`.  
   Optionally, you can push the image to your own ECR registry. To do this:
   - Build the image and tag it with the ECR registry URL:
     ```bash
     docker build -t cohere-ai/toolkit . -f standalone.Dockerfile
     docker tag cohere-ai/toolkit <Your ECR registry url>:latest
     ```
   If your PC is ARM processor-based, use this command to avoid architecture mismatch errors:
   ```bash
   docker buildx build --platform linux/amd64 -t cohere-ai/toolkit . -f standalone.Dockerfile
   docker tag cohere-ai/toolkit <Your ECR registry url>:latest
   ```
   - Push the image to the ECR registry:
     ```bash
     aws ecr get-login-password --region <Your AWS region> | docker login --username AWS --password-stdin <Your ECR registry url>
     docker push <Your ECR registry url>:latest
     ```

2. **Create Security Groups for Load Balancer**  
   Go to the EC2 dashboard, select Security Groups, and create a new security group with the following inbound rules:
   - Type: Custom TCP Rule, Port Range: 8000, Source: Anywhere IPv4
   - Type: Custom TCP Rule, Port Range: 4000, Source: Anywhere IPv4  
   Note the security group IDs for later use.

3. **Create Security Groups for ECS Instances**  
   Create a new security group with the following inbound rules:
   - Type: Custom TCP Rule, Port Range: 8000, Source: Security Group ID of the load balancer security group
   - Type: Custom TCP Rule, Port Range: 4000, Source: Security Group ID of the load balancer security group  
   Note the security group IDs for later use.

4. **Create Load Balancer**  
   Create a new load balancer with the following settings:
   - Type: Application Load Balancer
   - Listeners: HTTP:8000, HTTP:4000
   - Security Groups: Security Group ID of the load balancer security group created in step 2
   - Target Groups: Create a new target group with the following settings:
     - **API:**
       - Protocol: HTTP
       - Port: 8000
       - Health Check Path: /health
       - Health Check Port: traffic-port
       - Health Check Protocol: HTTP
       - Health Check Interval: 30 seconds
       - Health Check Timeout: 5 seconds
       - Healthy Threshold Count: 5
       - Unhealthy Threshold Count: 2
       - Target Type: IP addresses
       - Protocol Version: HTTP1
       - VPC: Default VPC
     - **Frontend:**
       - Protocol: HTTP
       - Port: 4000
       - Health Check Path: /
       - Health Check Port: traffic-port
       - Health Check Protocol: HTTP
       - Health Check Interval: 30 seconds
       - Health Check Timeout: 5 seconds
       - Healthy Threshold Count: 5
       - Unhealthy Threshold Count: 2
       - Target Type: IP addresses
       - Protocol Version: HTTP1
       - VPC: Default VPC  
     Note the target group ARNs, load balancer ARN, and load balancer DNS name for later use.

5. **Create ECS Cluster (Fargate)**  
   Create a new ECS cluster with the following settings:
   - Cluster name: ToolkitCluster  
   Note the cluster name for later use.

6. **Create ECS Task Definition**  
   Create a new ECS Task definition with the following settings:
   - Task Definition Name: ToolkitTask
   - Launch Type: Fargate
   - Operating System: Linux/X86_64
   - Task Memory: 8GB
   - Task CPU: 4 vCPU
   - Task Role: ecsTaskExecutionRole
   - Network Mode: awsvpc
   - Container Definitions: Add a new container with the following settings:
     - Name: ToolkitContainer
     - Image: \<Your ECR registry url\>/toolkit:latest or ghcr.io/cohere-ai/cohere-toolkit
     - Port Mappings: 8000:8000, 4000:4000
     - Environment Variables: COHERE_API_KEY=\<Your Cohere API key here\>
     - Environment Variables: NEXT_PUBLIC_API_HOSTNAME='http://\<Your load balancer DNS name\>:8000' from step 4  
   Note the task definition ARN and container name for later use.

7. **Create ECS Service Using AWS CLI**  
   Since the ECS console does not support creating a service with multiple target groups, follow these steps:
   - Modify the `ecs-service.json` file to include the correct values for your setup:
     - Service name
     - Cluster name from step 5
     - Target group ARNs from step 4
     - Container name from step 6
     - Task definition ARN from step 6
     - Subnet IDs from the default subnets in your VPC
     - Security group IDs from the security groups created in step 3
   - Run the following command to create the service:
     ```bash
     aws ecs create-service --service-name ToolkitService --region <Your AWS region> --cli-input-json file://ecs_service.json
     ```

After the service is created, you can access the Toolkit frontend at `http://<Your load balancer DNS name>:4000` and the API at `http://<Your load balancer DNS name>:8000/docs`.

You can follow these instructions to deploy the frontend and API separately by creating two separate services and load balancers.