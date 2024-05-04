![](/docs/assets/banner.png)

# Cohere Toolkit

Toolkit is a collection of prebuilt components enabling users to quickly build and deploy RAG applications.

- [Try Toolkit](#quick-start)
- [About Toolkit](#what-is-included-in-toolkit)
- [Deploy Toolkit](#deployment-guides)
- [Develop and troubleshoot](#setup-for-development)
- [Component Guides](#component-guides)
- [What's on our roadmap](#roadmap)
- [How to contribute](#contributing)
- [Try Coral Showcase](https://coral.cohere.com/)

![](/docs/assets/toolkit.gif)

## Quick start

Try the default Toolkit application yourself by deploying it in a container locally. You will need to have [Docker](https://www.docker.com/products/docker-desktop/) and [Docker-compose >= 2.22](https://docs.docker.com/compose/install/) installed.

```bash

docker run -e COHERE_API_KEY='>>YOUR_API_KEY<<' -p 8000:8000 -p 4000:4000 ghcr.io/cohere-ai/cohere-toolkit:latest

```

Go to localhost:4000 in your browser and start chatting with the model. This will use the model hosted on Cohere's platform. If you want to add your own tools or use another model, follow the instructions below to fork the repository.

### Building and running locally

Clone the repo and run

```bash
make first-run
```

Follow the instructions to configure the model - either AWS Sagemaker, Azure, or Cohere's platform. This can also be done by running `make setup` (See Option 2 below), which will help generate a file for you, or by manually creating a `.env` file and copying the contents of the provided `.env-template`. Then replacing the values with the correct ones.

#### Detailed environment setup

<details>
  <summary>Windows</summary>

1. Install [docker](https://docs.docker.com/desktop/install/windows-install/)
2. Install [git]https://git-scm.com/download/win
3. In PowerShell (Terminal), install [scoop](https://scoop.sh/). After installing, run scoop bucket add extras
4. Install pipx
```bash
scoop install pipx
pipx ensurepath
```
5. Install poetry >= 1.7.1 using 
```bash
pipx install poetry
```
6. Install miniconda using
```bash
scoop install miniconda3
conda init powershell
```
7. Restart PowerShell
8. Install the following:
```bash
scoop install postgresql
scoop install make
```
9. Create a new virtual environment with Python 3.11
```bash
conda create -n toolkit python=3.11
conda activate toolkit
```
10. Clone the repo
11. Alternatively to `make first-run` or `make setup`, run
```bash
poetry install --only setup --verbose
poetry run python cli/main.py
make migrate
make dev
```
12. Navigate to https://localhost:4000 in your browser

</details>

<details>
  <summary>MacOS</summary>

1. Install Xcode. This can be done from the App Store or terminal 
```bash
xcode-select --install
```
2. Install [docker desktop](https://docs.docker.com/desktop/install/mac-install/)
3. Install [homebrew](https://brew.sh/)
4. Install [pipx](https://github.com/pypa/pipx). This is useful for installing poetry later.
```bash
brew install pipx
pipx ensurepath
```
5. Install [postgres](brew install postgresql)
6. Install conda using [miniconda](https://docs.anaconda.com/free/miniconda/index.html)
7. Use your environment manager to create a new virtual environment with Python 3.11
```bash
conda create -n toolkit python=3.11
```
8. Install [poetry >= 1.7.1](https://python-poetry.org/docs/#installing-with-pipx)
```bash
pipx install poetry
```
To test if poetry has been installed correctly,
```bash
conda activate toolkit
poetry --version
```
You should see the version of poetry (e.g. 1.8.2). If poetry is not found, try
```bash
export PATH="$HOME/.local/bin:$PATH"
```
And then retry `poetry --version`
9. Clone the repo and run `make first-run`
10. Navigate to https://localhost:4000 in your browser

</details>

<details>
  <summary>Environment variables</summary>
  
### Cohere Platform

- `COHERE_API_KEY`: If your application will interface with Cohere's API, you will need to supply an API key. Not required if using AWS Sagemaker or Azure.
  Sign up at https://dashboard.cohere.com/ to create an API key.
- `NEXT_PUBLIC_API_HOSTNAME`: The backend URL which the frontend will communicate with. Defaults to http://backend:8000 for use with `docker compose`
- `DATABASE_URL`: Your PostgreSQL database connection string for SQLAlchemy, should follow the format `postgresql+psycopg2://USER:PASSWORD@HOST:PORT`.

### AWS Sagemaker

To use the toolkit with AWS Sagemaker you will first need the cohere model (a command version) which powers chat deployed in Sagemaker. Follow Cohere's [guide](https://docs.cohere.com/docs/amazon-sagemaker-setup-guide) and [notebooks](https://github.com/cohere-ai/cohere-aws/tree/main/notebooks/sagemaker) to deploy a command model and create an endpoint which can then be used with the toolkit.

Then you will need to set up authorization, [see more details here](https://aws.amazon.com/iam/). The default toolkit set up uses the configuration file (after `aws configure sso`) with the following environment variables:

- `SAGE_MAKER_REGION_NAME`: The region you configured for the model.
- `SAGE_MAKER_ENDPOINT_NAME`: The name of the endpoint which you created in the notebook.
- `SAGE_MAKER_PROFILE_NAME`: Your AWS profile name

### Hosted tools

- `PYTHON_INTERPRETER_URL`: URL to the python interpreter container. Defaults to http://localhost:8080.
- `TAVILY_API_KEY`: If you want to enable internet search, you will need to supply a Tavily API Key. Not required.

</details>

### Deploy locally

Once your environment variables are set, you're ready to deploy the Toolkit locally! Pull the Docker images from Github Artifact registry or build files from source. See the `Makefile` for all available commands.

Requirements:

- [Docker](https://www.docker.com/products/docker-desktop/)
- [Poetry](https://python-poetry.org/docs/#installation)
- [Docker-compose >= 2.22](https://docs.docker.com/compose/install/)
- [Postgres](https://www.postgresql.org/download/)

#### Option 1 - Install locally with Docker:

Ensure your shell is authenticated with [GHCR](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry#authenticating-with-a-personal-access-token-classic).

Pull the [Single Container Image](docs/deployment_guides/single_container.md) from Github's Artifact Registry

```bash
docker pull ghcr.io/cohere-ai/cohere-toolkit:latest
```

Run the images locally:

```bash
docker run --name=cohere-toolkit -itd -e COHERE_API_KEY='Your Cohere API key here' -p 8000:8000 -p 4000:4000 ghcr.io/cohere-ai/cohere-toolkit
```

#### Option 2 - Build locally from scratch:

##### Option 2.1 - Run everything at once

Run `make first-run` to start the CLI, that will generate a `.env` file for you. This will also run all the DB migrations and run the containers

```bash
make first-run
```

##### Option 2.1 - Run each command separately

Run `make setup` to start the CLI, that will generate a `.env` file for you:

```bash
make setup
```

Then run:

```bash
make migrate
make dev
```

If you did not change the default port, visit http://localhost:4000/ in your browser to chat with the model.

## What is included in Toolkit?

Components in this repo include:

- `src/interfaces/coral_web` - A web app built in Next.js. Includes a simple SQL database out of the box to store conversation history in the app.
- `src/backend` - Contains preconfigured data sources and retrieval code to set up RAG on custom data sources (called "Retrieval Chains"). Users can also configure which model to use, selecting from Cohere's models hosted on either Cohere's platform, Azure, and AWS Sagemaker. By default, we have configured a Langchain data retriever to test RAG on Wikipedia and your own uploaded documents.

![](/docs/assets/toolkit_graphic.png)

## Deployment Guides

Looking to serve your application in production? Deploy the Toolkit to your preferred cloud provider by following our guides below:

### Other deployment options
- [Single Container Setup](docs/deployment_guides/single_container.md): Useful as a quickstart to run the Toolkit, or deploy to AWS on an EC2 instance.
- [AWS ECS Fargate Deployment](docs/deployment_guides/aws_ecs_single_container.md): Deploy the Toolkit single container to AWS ECS(Fargate).
- [AWS ECS EC2 Deployment](docs/deployment_guides/aws_ecs_single_container_ec2.md): Deploy the Toolkit single container to AWS ECS(EC2).
- [Google Cloud Platform](docs/deployment_guides/gcp_deployment.md): Help setup your Cloud SQL instance, then build, push and deploy backend+frontend containers to Cloud Run.

### Deploying to Azure

You can deploy Toolkit with one click to Microsoft Azure Platform:

[<img src="https://aka.ms/deploytoazurebutton" height="48px">](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fcohere-ai%2Fcohere-toolkit%2Fmain%2Fazuredeploy.json)

This deployment type uses Azure Container Instances to host the Toolkit.
After your deployment is complete click "Go to resource" button.
1) Check the logs to see if the container is running successfully:
   - click on the "Containers" button on the left side of the screen
   - click on the container name
   - click on "Logs" tab to see the logs
2) Navigate to the "Overview" tab to see the FQDN of the container instance
3) Open the \<FQDN\>:4000 in your browser to access the Toolkit

## Setup for Development

### Setting up Poetry

Use for configuring and adding new retrieval chains.

Install your dependencies:

```bash
poetry install
```

Run linters:

```bash
poetry run black .
poetry run isort .
```

## Setting up the Environment Variables
**Please confirm that you have at least one configuration of the Cohere Platform, SageMaker or Azure.**

You have two methods to set up the environment variables:
1. Run `make setup` and follow the instructions to configure it.
2. Run `cp .env-template .env` and adjust the values in the `.env` file according to your situation.

### Setting up Your Local Database

The docker-compose file should spin up a local `db` container with a PostgreSQL server. The first time you setup this project, and whenever new migrations are added, you will need to run:

```bash
make migrate
```

This will apply all existing database migrations and ensure your DB schema is up to date.

If ever you run into issues with Alembic, such as being out of sync and your DB does not contain any data you'd like to preserve, you can run:

```bash
make reset-db
make migrate
make dev
```

This will delete the existing `db` container volumes, restart the containers and reapply all migrations.

### Testing the Toolkit

Run:

```bash
make dev
```

To spin the `test_db` service for you. After, you can run:

```bash
make run-tests
```

### Making Database Model Changes

When making changes to any of the database models, such as adding new tables, modifying or removing columns, you will need to create a new Alembic migration. You can use the following Make command:

```bash
make migration
```

Important: If adding a new table, make sure to add the import to the `model/__init__.py` file! This will allow Alembic to import the models and generate migrations accordingly.

This should generate a migration on the Docker container and be copied to your local `/alembic` folder. Make sure the new migration gets created.

Then you can migrate the changes to the PostgreSQL Docker instance using:

```bash
make migrate
```

### Troubleshooting

#### Community features are not accessible

Make sure you add `USE_COMMUNITY_FEATURES=True` to your .env file.


#### Multiple errors after running make dev for the first time

Make sure you run the following command before running make dev:

```bash
make migrate
```


#### Error: pg_config executable not found.

Make sure that all requirements including postgres are properly installed.

If you're using MacOS, run:
```bash
brew install postgresql
```

For other operating systems, you can check the [postgres documentation](https://www.postgresql.org/download/).


#### Debugging locally

To debug any of the backend logic while the Docker containers are running, you can run:

```bash
make dev
```

This will run the Docker containers with reloading enabled, then in a separate shell window, run:

```bash
make attach
```

This will attach an interactive shell to the backend running, now when your backend code hits any

```python
import pdb; pdb.set_trace()
```

it will allow you to debug.

## Component Guides

### How to use community features

By default, the toolkit runs without community tools or deployments. If you want to enable them, add the following to the .env file or use `make setup` to set this variable:

```bash
USE_COMMUNITY_FEATURES=True
```

### How to add your own model deployment

A model deployment is a running version of one of the Cohere command models. The Toolkit currently supports the model deployments:

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

### How to call the backend as an API

It is possible to just run the backend service, and call it in the same manner as the Cohere API. Note streaming and non streaming endpoints are split into 'http://localhost:8000/chat-stream' and 'http://localhost:8000/chat' compared to the API. For example, to stream:

```bash
curl --location 'http://localhost:8000/chat-stream' \
--header 'User-Id: me' \
--header 'Content-Type: application/json' \
--data '{
    "message": "Tell me about the aya model"
}
'
```

### How to add your own chat interface

Currently the core chat interface is the Coral frontend. To add your own interface, take the steps above for call the backend as an API in your implementation and add it alongside `src/community/interfaces/`.

### How to add a connector to the Toolkit

If you have already created a [connector](https://docs.cohere.com/docs/connectors), it can be used in the toolkit with `ConnectorRetriever`. Add in your configuration and then add the definition in [community/config/tools.py](https://github.com/cohere-ai/cohere-toolkit/blob/main/src/community/config/tools.py) similar to `Arxiv` implementation with the category `Category.DataLoader`. You can now use the Coral frontend and API with the connector.

### How to set up web search with the Toolkit

To use Coral with web search, simply use the `Tavily_Internet_Search` tool by adding your API key to the env file. Alternatively you can use any search provider of your choosing, either with your own implementation or an integration implementation (such as LangChain) by following these [steps below](#how-to-create-your-own-tools-and-retrieval-sources).

### How to set up PDF Upload with the Toolkit

To use Coral with document upload, simply use the `File_Upload_LlamaIndex` or `File_Upload_Langchain` (this needs a cohere API key in the .env file) tool or by adding your API key to the env file. Alternatively you can use any document uploader of your choosing, either with your own implementation or an integration implementation (such as LangChain) by following these [steps below](#how-to-create-your-own-tools-and-retrieval-sources).

### How to create your own tools and retrieval sources

Toolkit includes some sample tools that you can copy to configure your own data sources:

- File loaders - Parses a PDF file and performs RAG. Enables users to upload PDF in Toolkit UI. Users have an option to use either Langchain or Llamaindex, whichever is preferred. Langchain is used by default.
- Data loaders - This tool queries a data source and then performs RAG on extracted documents. We used Langchain's Wikiretriever as the sample data source.
- Functions - Python interpreter and calculator tools.

To create your own tools or add custom data sources, see our guide: [tools and retrieval sources overview](/docs/custom_tool_guides/tool_guide.md)


## Themeing and customization

### Changing the color scheme, font and other styles

To change the color scheme of the Coral frontend, there are a few options:

- Modify the `src/interfaces/coral_web/src/themes/cohereTheme.js` with a new color scheme. For example, to change the primary color scheme:

```js
primary: {
          ...
          600: '#E25D41',
          500: '#AE4359', // Changed from default color
          400: '#FF967E',
          ...
        },
```

- Add a new theme to the `src/interfaces/coral_web/src/themes` folder and update the `src/interfaces/coral_web/tailwind.config.js` to include the new theme:

```js
module.exports = {
  presets: [require('./src/themes/yourTheme')],
  ...
}
```

Similarly, you can change the font, font size, and other styles in the theme file or add a new theme file.

After updating the theme, you will need to rebuild the frontend to see the changes.

## Experimental Features

**Please note that these are experimental features.**

### Langchain Multihop

Chatting with multihop tool usage through Langchain is enabled by setting experimental feature flag to True in `.env`. 

```bash
USE_EXPERIMENTAL_LANGCHAIN=True
```

By setting this flag to true, only tools that have a Langchain implementation can be utilized. 
These exist under `LANGCHAIN_TOOLS` and require a `to_lanchain_tool()` function on the tool implementation which returns a langchain compatible tool. 
Python interpreter and Tavily Internet search are provided in the toolkit by default once the environment is set up.

Example API call:
```bash
curl --location 'http://localhost:8000/langchain-chat' \
--header 'User-Id: me' \
--header 'Content-Type: application/json' \
--data '{
    "message": "Tell me about the aya model",
    "tools": [{"name": "Python_Interpreter"},{"name": "Internet Search"},]
}'
```

Currently, citations are not supported in lanchain multihop.

## Roadmap

1. Set env variables in UI
2. Include citations for multi hop tools
3. Display images for python interpreter tool
4. Add a slack bot as an available interface
5. White labelling: Changing fonts, logos, and colours.
6. User management and authentication system: Toolkit is currently configured with one user role and no authentication.

## Contributing

Contributions are what drive an open source community, any contributions made are greatly appreciated. To get started, check out our [documentation.](CONTRIBUTING.md)
