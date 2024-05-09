# Services Deployment Guides

Looking to serve your application in production? Deploy the Toolkit to your preferred cloud provider by following our guides below:

## Services Deployment Options
- [Single Container Setup](deployment_guides/single_container.md): Useful as a quickstart to run the Toolkit, or deploy to AWS on an EC2 instance.
- [AWS ECS Fargate Deployment](deployment_guides/aws_ecs_single_container.md): Deploy the Toolkit single container to AWS ECS(Fargate).
- [AWS ECS EC2 Deployment](deployment_guides/aws_ecs_single_container_ec2.md): Deploy the Toolkit single container to AWS ECS(EC2).
- [Google Cloud Platform](deployment_guides/gcp_deployment.md): Help setup your Cloud SQL instance, then build, push and deploy backend+frontend containers to Cloud Run.
- Deploying to Azure. You can deploy Toolkit with one click to Microsoft Azure Platform: [<img src="https://aka.ms/deploytoazurebutton" height="24px">](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fcohere-ai%2Fcohere-toolkit%2Fmain%2Fazuredeploy.json).  This deployment type uses Azure Container Instances to host the Toolkit. After your deployment is complete click "Go to resource" button.
   1) Check the logs to see if the container is running successfully:
      - click on the "Containers" button on the left side of the screen
      - click on the container name
      - click on "Logs" tab to see the logs
   2) Navigate to the "Overview" tab to see the FQDN of the container instance
   3) Open the \<FQDN\>:4000 in your browser to access the Toolkit