# Command Model Provider Guides

A **model deployment** refers to an active instance of one of the Cohere command models. The Toolkit currently supports the following model deployment options:

## Command Model Provider Options

- **Cohere Platform** (`model_deployments/cohere_platform.py`)
  - This deployment option utilizes the [Cohere Python SDK](https://github.com/cohere-ai/cohere-python) to interface with the Cohere Platform. You will need a Cohere API key, which is automatically generated when you create an account. You can find your API key [here](https://dashboard.cohere.com/api-keys).

- **Azure** (`model_deployments/azure.py`)
  - This option connects to your Azure deployment. To set up an Azure deployment, follow the instructions [here](https://learn.microsoft.com/en-us/azure/ai-studio/how-to/deploy-models-cohere-command). After deploying a model, retrieve the endpoint URL and API key from Azure AI Studio: navigate to [https://ai.azure.com/build/](https://ai.azure.com/build/) -> Project -> Deployments -> Click your deployment to access the URL and API Key. Remember to append `/v1` to the endpoint URL when using the Cohere SDK.

- **SageMaker** (`model_deployments/sagemaker.py`)
  - This deployment option connects to your SageMaker endpoint. For setup instructions, refer to the [SageMaker setup guide](https://docs.cohere.com/docs/amazon-sagemaker-setup-guide) or use the command notebook available [here](https://github.com/cohere-ai/cohere-aws/tree/main/notebooks/sagemaker). Note your AWS region and endpoint name when executing the notebook, as these will be required as environment variables.

- **Local Models with LlamaCPP** (`community/model_deployments/local_model.py`)
  - This option enables the use of a local model. To implement this deployment, download a model of your choice. You can use Cohere command models or explore other available models [here](https://github.com/ggerganov/llama.cpp). Enable community features by setting `USE_COMMUNITY_FEATURES=True` in your `.env` file.

## Adding Your Own Deployment

1. Create a deployment file and place it in the [/community/model_deployments](https://github.com/cohere-ai/cohere-toolkit/tree/main/src/community/model_deployments) folder. Implement the function calls from `BaseDeployment`, mirroring the existing deployment structures.
2. Register your deployment in [src/community/config/deployments.py](https://github.com/cohere-ai/cohere-toolkit/blob/main/src/community/config/deployments.py).
3. Add any required environment variables to the `.env` template.

## Adding a Cohere Private Deployment

To add a Cohere private deployment, replicate the steps above for the Cohere Platform implementation, adjusting the `base_url` for your private deployment and incorporating any custom authentication steps.