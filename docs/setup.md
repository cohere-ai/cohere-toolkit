# Setup the toolkit

## Quick start

Try the default Toolkit application yourself by deploying it in a container locally. You will need to have [Docker](https://www.docker.com/products/docker-desktop/) and [Docker-compose >= 2.22](https://docs.docker.com/compose/install/) installed.

```bash
docker run -e COHERE_API_KEY='>>YOUR_API_KEY<<' -p 8000:8000 -p 4000:4000 ghcr.io/cohere-ai/cohere-toolkit:latest
```

If you need to use community features, you can run the container with the following command:

```bash
docker run -e INSTALL_COMMUNITY_DEPS='true' -e COHERE_API='>>YOUR_API_KEY<<' -p 8000:8000 -p 4000:4000 ghcr.io/cohere-ai/cohere-toolkit:latest
```

Go to localhost:4000 in your browser and start chatting with the model. This will use the model hosted on Cohere's platform. If you want to add your own tools or use another model, follow the instructions below to fork the repository.

### Building and running locally

Clone the repo and run

```bash
make first-run
```

Follow the instructions to configure the model - either AWS Sagemaker, Bedrock, Azure, or Cohere's platform. This can also be done by running `make setup` (See Option 2 below), which will help generate a file for you, or by manually creating a `.env` file and copying the contents of the provided `.env-template`. Then replacing the values with the correct ones.
For Windows systems see the detailed setup below.

#### Detailed environment setup

<details>
  <summary>Windows</summary>

1. Install [docker](https://docs.docker.com/desktop/install/windows-install/)
2. Install [git]https://git-scm.com/download/win
3. In PowerShell (Terminal), install [scoop](https://scoop.sh/). After installing, run the following commands:

```bash
scoop bucket add extras
```

4. Install miniconda using

```bash
scoop install miniconda3
conda init cmd.exe
```

5. Restart PowerShell
6. Install the following:

```bash
scoop install postgresql
scoop install make
```

7. Create a new virtual environment with Python 3.11 using CMD terminal

```bash
conda create -n toolkit python=3.11
conda activate toolkit
```

8. Install poetry == 1.7.1 using

```bash
pip install poetry==1.7.1
```

9. Clone the repo
10. Alternatively to `make win-first-run` or `make win-setup`, run

```bash
poetry install --with setup,community --verbose
poetry run python src/backend/cli/main.py
make migrate
make dev
```

11. Navigate to https://localhost:4000 in your browser

### Possible issues

- If you encounter on error on running `poetry install` related to `llama-cpp-python`, please run the following command:

```bash
poetry source add llama-cpp-python https://abetlen.github.io/llama-cpp-python/whl/cpu
poetry source add pypi
poetry lock
```

and then run the commands in step 10 again.
For more information and additional installation instructions, see [llama-cpp-python documentation](https://github.com/abetlen/llama-cpp-python)

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

And then retry `poetry --version` 9. Clone the repo and run `make first-run` 10. Navigate to https://localhost:4000 in your browser

</details>

<details>
  <summary>Environment variables</summary>
  
### Cohere Platform

- `COHERE_API_KEY`: If your application will interface with Cohere's API, you will need to supply an API key. Not required if using AWS Sagemaker or Azure.
  Sign up at https://dashboard.cohere.com/ to create an API key.
- `NEXT_PUBLIC_API_HOSTNAME`: The backend URL which the frontend will communicate with. Defaults to http://backend:8000 for use with `docker compose`
- `FRONTEND_HOSTNAME`: The URL for the frontend client. Defaults to http://localhost:4000
- `DATABASE_URL`: Your PostgreSQL database connection string for SQLAlchemy, should follow the format `postgresql+psycopg2://USER:PASSWORD@HOST:PORT`.
- `REDIS_URL`: Your Redis connection string, should follow the format `redis://USER:PASSWORD@HOST:PORT`.

### AWS Sagemaker

To use the toolkit with AWS Sagemaker you will first need the cohere model (a command version) which powers chat deployed in Sagemaker. Follow Cohere's [guide](https://docs.cohere.com/docs/amazon-sagemaker-setup-guide) and [notebooks](https://github.com/cohere-ai/cohere-aws/tree/main/notebooks/sagemaker) to deploy a command model and create an endpoint which can then be used with the toolkit.

Then you will need to set up authorization, [see more details here](https://aws.amazon.com/iam/). The default toolkit set up uses the configuration file (after `aws configure sso`) with the following environment variables:

- `SAGE_MAKER_REGION_NAME`: The region you configured for the model.
- `SAGE_MAKER_ENDPOINT_NAME`: The name of the endpoint which you created in the notebook.
- `SAGE_MAKER_PROFILE_NAME`: Your AWS profile name

### Bedrock

- `BEDROCK_ACCESS_KEY`: Your Bedrock access key.
- `BEDROCK_SECRET_KEY`: Your Bedrock secret key.
- `BEDROCK_SESSION_TOKEN`: Your Bedrock session token.
- `BEDROCK_REGION_NAME`: The region you configured for the model.

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

Pull the [Single Container Image](deployment_guides/single_container.md) from Github's Artifact Registry

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

## Setup for Development

### Setting up Poetry

Use for configuring and adding new retrieval chains.

Install your development dependencies:

```bash
poetry install --with dev
```

If you also need to install the community features, run:

```bash
poetry install --with community
```

To run linters, you can use `make lint` or separate commands:

```bash
poetry run black .
poetry run isort .
```

Run type checker:

- See docs for [pyright](https://microsoft.github.io/pyright/)
- Install with `conda install pyright`
- Run with `pyright`
- Configure in [pyproject.toml](../pyproject.toml) under `[tool.pyright]`

## Setting up the Environment Variables

**Please confirm that you have at least one configuration of the Cohere Platform, SageMaker, Bedrock or Azure.**

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
