## Amazon Elastic Container Service(ECS) Deployment

Requirements:
- AWS account
- Docker installed
- Docker Image of the Toolkit from the public registry
- Cohere API key
- AWS CLI installed and configured
- VPC
- Subnets
- Security groups
- EC2
- ECS Cluster
- ECS Task definition
- ECS Service
Optional requirements:
- Route 53 domain name - if you want to use a custom domain name
- ECR registry to deploy image to

Please note that this is a sample deployment, and it's not recommended for production use.
To deploy the Toolkit to AWS ECS EC2, you can follow the steps below:
1) The Toolkit Docker image is available on the public registry at `ghcr.io/cohere-ai/cohere-toolkit`.
   Optionally, you can push the image to your own ECR registry.
   To do it do the following:
    - Build the Image and Tag it with the ECR registry URL:
    ```bash
       docker build -t cohere-ai/toolkit . -f standalone.Dockerfile
       docker tag cohere-ai/toolkit <Your ECR registry url>:latest
   ```
   If your PC is ARM processor based, you can use the following command to build the image to avoid architecture mismatch error:
   ```bash
    docker buildx build --platform linux/amd64 -t cohere-ai/toolkit . -f standalone.Dockerfile
    docker tag cohere-ai/toolkit <Your ECR registry url>:latest
    ```
    - Push the image to the ECR registry:
    ```bash
     aws ecr get-login-password --region <Your AWS region> | docker login --username AWS --password-stdin <Your ECR registry url>
     docker push <Your ECR registry url>:latest
    ```
   
2) Create a new ECS cluster(EC2) with the following settings:
    - Cluster name: ToolkitCluster
    - Infrastructure: Amazon EC2 instances
    - Auto Scaling group (ASG): Create new ASG
    - Provisioning: On-Demand Instance or Spot Instance (the On-demand instance is recommended)
    - Container instance Amazon Machine Image (AMI) - Amazon Linux 2(kernel 5.10)
    - EC2 Instance type: t3.xlarge
    - EC2 Instance role: ecsInstanceRole or Create New Role
    - Desired capacity: Minimum - 1 Maximum - 1
    - Network settings for Amazon EC2 instances: 
      - VPC: Select your VPC
      - Subnets: Select your subnets
      - Security group: Create a new security group with the following inbound rules:
        - Type: Custom TCP Rule, Port Range: 8000, Source: Anywhere IPv4
        - Type: Custom TCP Rule, Port Range: 4000, Source: Anywhere IPv4
      - Auto-assign public IP: Turn On
    After the cluster is created, navigate to EC2 dashboard, select the created instance, and note the Public IPv4 DNS for later use.
3) Create a new ECS Task definition with the following settings:
    - Task definition family: ToolkitTask
    - Launch Type: Amazon EC2 instances
    - Operating System: Linux/X86_64
    - Network Mode: host
    - Task CPU: 3 vCPU
    - Task Memory: 12 GB
    - Task Execution Role: Create new or ecsTaskExecutionRole
    - Container Definitions: Add a new container with the following settings:
        - Name: ToolkitContainer
        - Image: \<Your ECR registry url\>/toolkit:latest or ghcr.io/cohere-ai/cohere-toolkit:latest
        - Port Mappings: TCP 8000:8000, 4000:4000 App protocol: HTTP
        - CPU: 3 vCPU
        - Memory soft limit: 8 GB
        - Memory hard limit: 12 GB
        - Environment Variables: COHERE_API_KEY=\<Your Cohere API key here\>
        - Environment Variables: NEXT_PUBLIC_API_HOSTNAME='http://\<Your EC2 instance Public IPv4 DNS\>:8000' from step 2
        - Contaner timeouts:
          - start timeout: 2
          - stop timeout: 120
4) Create a new ECS service. To do this, you can do the following:
    - Click Deploy -> Create Service on the notification message or navigate to the ECS dashboard select your cluster and click Create on the Services tab.
    - Existing cluster - Select your cluster
    - Compute options - Launch type
    - Launch type - EC2
    - Task definition: Family - ToolkitTask
    - Deployment Configuration:
        - Application type: Service
        - Service name: ToolkitService
        - Service type: REPLICA
        - Desired tasks: 1
    - Deployment options:
        - Deployment type: Rolling update
        - Min running tasks %: 100
        - Max running tasks %: 200
    
    Click Create button to create the service.
      
After the service is created, check that the Service task is running and after that 
you can access the Toolkit frontend at `http://<Your EC2 instance Public IPv4 DNS>:4000` and the API at `http://<Your EC2 instance Public IPv4 DNS>:8000/docs`.

Please note you can follow these instructions to deploy the frontend and API separately by creating two separate services.
