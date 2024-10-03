# Services Deployment Guides

Looking to serve your application in production? Deploy the Toolkit to your preferred cloud provider by following our guides below:

## Services Deployment Options

1. **[Single Container Setup](deployment_guides/single_container.md)**  
   Useful as a quickstart to run the Toolkit or deploy to AWS on an EC2 instance.

2. **[AWS ECS Fargate Deployment](deployment_guides/aws_ecs_single_container.md)**  
   Deploy the Toolkit single container to AWS ECS (Fargate).

3. **[AWS ECS EC2 Deployment](deployment_guides/aws_ecs_single_container_ec2.md)**  
   Deploy the Toolkit single container to AWS ECS (EC2).

4. **[Google Cloud Platform](deployment_guides/gcp_deployment.md)**  
   Help setup your Cloud SQL instance, then build, push, and deploy backend + frontend containers to Cloud Run.

5. **[One Click Deploy to GCP](deployment_guides/gcp_one_click_deployment.md)** 
   [![Run on Google Cloud](https://deploy.cloud.run/button.svg)](https://deploy.cloud.run?dir=/)
   - After clicking the above, continue the steps in the linked guide.

6. **Deploying to Azure Container Instance**  
   You can deploy the Toolkit with one click to Microsoft Azure Platform:  
   [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fcohere-ai%2Fcohere-toolkit%2Fmain%2Fazuredeploy.json)  
   - After your deployment is complete, click the "Go to resource" button.
   - Check the logs to see if the container is running successfully:
     - Click on the "Containers" button on the left side of the screen.
     - Click on the container name.
     - Click on the "Logs" tab to see the logs.
   - Navigate to the "Overview" tab to see the FQDN of the container instance.
   - Open the `<FQDN>:4000` in your browser to access the Toolkit.

7. **Deploying to Azure Cloud App**  
   You can deploy the Toolkit with one click to Microsoft Azure Platform:  
   [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fcohere-ai%2Fcohere-toolkit%2Fmain%2Fazuredeploy.hpa.json)  
   - Select your subscription and resource group. If you don't have a resource group, create a new one.
   - Enter the connection string in the format:  
     `postgresql+psycopg2://USERNAME:PASSWORD@HOST:PORT/DB_NAME`  
     Ensure `HOST` is the Public IP or DNS name of your PostgreSQL database.
   - Enter your Cohere API key.
   - Click "Review + create" and then "Create" to deploy the Toolkit.
   - After the deployment, click on the "Go to resource group" button.
   - Click on the Toolkit container app.
   - Click on the "Overview" tab to see the "Application URL" of the container app.
   - Navigate to the "Application URL" to access the Toolkit.

   To scale the Toolkit, you can enable Automatic Horizontal Scaling by following this [tutorial](https://learn.microsoft.com/en-us/azure/container-apps/tutorial-scaling).
