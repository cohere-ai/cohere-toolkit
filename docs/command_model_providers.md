# Command Model Provider Guides

A model deployment is a running version of one of the Cohere command models. The Toolkit currently supports the model deployments:

## Command Model Provider Options

- Cohere Platform (model_deployments/cohere_platform.py)
  - This model deployment option call the Cohere Platform with the [Cohere python SDK](https://github.com/cohere-ai/cohere-python). You will need a Cohere API key. When you create an account with Cohere, we automatically create a trial API key for you. You can find it [here](https://dashboard.cohere.com/api-keys).
- Azure (model_deployments/azure.py)
  - This model deployment calls into your Azure deployment. To get an Azure deployment [follow these steps](https://learn.microsoft.com/en-us/azure/ai-studio/how-to/deploy-models-cohere-command). Once you have a model deployed you will need to get the endpoint URL and API key from the azure AI studio https://ai.azure.com/build/ -> Project -> Deployments -> Click your deployment -> You will see your URL and API Key. Note to use the Cohere SDK you need to add `/v1` to the end of the url.
- SageMaker (model_deployments/sagemaker.py)
  - This deployment option calls into your SageMaker deployment. To create a SageMaker endpoint [follow the steps here](https://docs.cohere.com/docs/amazon-sagemaker-setup-guide), alternatively [follow a command notebook here](https://github.com/cohere-ai/cohere-aws/tree/main/notebooks/sagemaker). Note your region and endpoint name when executing the notebook as these will be needed in the environment variables.
- Local models with LlamaCPP (community/model_deployments/local_model.py)
  - This deployment option calls into a local model. To use this deployment you will need to download a model. You can use Cohere command models or choose between a range of other models that you can see [here](https://github.com/ggerganov/llama.cpp). You will need to enable community features to use this deployment by setting `USE_COMMUNITY_FEATURES=True` in your .env file.
- To add your own deployment:
  1. Create a deployment file, add it to [/community/model_deployments](https://github.com/cohere-ai/cohere-toolkit/tree/main/src/community/model_deployments) folder, implement the function calls from `BaseDeployment` similar to the other deployments.
  2. Add the deployment to [src/community/config/deployments.py](https://github.com/cohere-ai/cohere-toolkit/blob/main/src/community/config/deployments.py)
  3. Add the environment variables required to the env template.
- To add a Cohere private deployment, use the steps above copying the cohere platform implementation changing the base_url for your private deployment and add in custom auth steps.