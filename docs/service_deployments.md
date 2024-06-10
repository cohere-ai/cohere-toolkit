# Services Deployment Guides

Looking to serve your application in production? Deploy the Toolkit to your preferred cloud provider by following our guides below:

## Services Deployment Options
- [Single Container Setup](deployment_guides/single_container.md): Useful as a quickstart to run the Toolkit, or deploy to AWS on an EC2 instance.
- [AWS ECS Fargate Deployment](deployment_guides/aws_ecs_single_container.md): Deploy the Toolkit single container to AWS ECS(Fargate).
- [AWS ECS EC2 Deployment](deployment_guides/aws_ecs_single_container_ec2.md): Deploy the Toolkit single container to AWS ECS(EC2).
- [Google Cloud Platform](deployment_guides/gcp_deployment.md): Help setup your Cloud SQL instance, then build, push and deploy backend+frontend containers to Cloud Run.
- [One Click Deploy to GCP](deployment_guides/gcp_one_click_deployment.md): Help setup your container to Cloud Run.
- Deploying to Azure Container Instance. You can deploy Toolkit with one click to Microsoft Azure Platform: [<img src="https://aka.ms/deploytoazurebutton" height="24px">](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fcohere-ai%2Fcohere-toolkit%2Fmain%2Fazuredeploy.json).
  This deployment type uses Azure Container Instances to host the Toolkit. After your deployment is complete click "Go to resource" button.
   - Check the logs to see if the container is running successfully:
      - click on the "Containers" button on the left side of the screen
      - click on the container name
      - click on "Logs" tab to see the logs
   - Navigate to the "Overview" tab to see the FQDN of the container instance
   - Open the \<FQDN\>:4000 in your browser to access the Toolkit
- Deploying to Azure Cloud App. You can deploy Toolkit with one click to Microsoft Azure Platform: [<img src="https://aka.ms/deploytoazurebutton" height="24px">](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fcohere-ai%2Fcohere-toolkit%2Fmain%2Fazuredeploy.hpa.json).  
  This deployment type uses Azure Container App to host the Toolkit. Follow these steps to deploy the Toolkit:
   - Select your subscription and resource group. If you don't have a resource group, create a new one.
   - Enter the connection string of the format `postgresql+psycopg2://USERNAME:PASSWORD@HOST:PORT/DB_NAME`. 
      The `HOST` value here is the Public IP address or DNS name of your provisioned PostgreSQL database, and the default `PORT` is 5432. 
      Make sure to use the username and password pair you set when creating your SQL instance. For example, `postgresql+psycopg2://myuser:mypassword@<your-db-public-ip-address>:5432/toolkit`.
   - Enter your Cohere API key.
   - Click "Review + create" and then "Create" to deploy the Toolkit.
   - After the deployment is complete, click on the "Go to resource group" button.
   - Click on the Toolkit container app.
   - Click on the "Overview" tab to see the "Application Url" of the container app.
   - Navigate to the "Application Url" to access the Toolkit.
  
   To scale the Toolkit, you can enable the Automatic Horizontal Scaling by following this [tutorial](https://learn.microsoft.com/en-us/azure/container-apps/tutorial-scaling).

    

