# GitHub Actions for Automated DB Migrations

This guide provides instructions for setting up a GitHub Action to automatically run database migrations whenever you push changes to your repository.

## Prerequisites
To set up the GitHub Action, ensure you have the following:
- Admin permissions for the repository where you want to implement the action.
- Access to a database where migrations will be executed.

## Steps to Set Up GitHub Actions

### Overview
This guide covers different methods for executing migrations:
- Running migrations using SSH access to a remote server.
- Running migrations on a remote database using connection strings.
- Running migrations on a remote database via the Cohere Toolkit's API migrations endpoint.

### Setting Up the GitHub Environment and Secrets
Follow these steps to configure the GitHub environment and secrets:
1. Navigate to your repository on GitHub.
2. Click on the `Settings` tab.
3. Select the `Environments` menu on the left.
4. Click on the `New environment` button or choose an existing environment (we will use the `Production` environment in this guide).
5. Enter the environment name and click on the `Configure environment` button.
6. (Optional) Set rules for the environment, such as restricting the `Production` environment to the `main` branch.
7. Click on the `Add secret` button to define the required secrets.

### Running Migrations Using SSH Access
To run migrations via SSH to a remote server, set up the following secrets:
- **`SSH_PRIVATE_KEY`**: The private key for SSH authentication.
- **`SSH_HOST`**: The hostname or IP address of the remote server.
- **`SSH_PORT`**: The port for SSH authentication.
- **`SSH_USER_NAME`**: The username for SSH authentication.

Use the sample GitHub Action workflow file located at `.github/workflows/run_alembic_migrations.yml`. Set the `SSH_PROJECT_DIR` variable to the path of your project directory on the remote server. 

The action scripts are located in the `.github/scripts` directory:
- **`run_docker_migration.sh`**: Executes migrations using Docker.
- **`run_src_migration.sh`**: Executes migrations using the source code.

**Note**: 
- If the Toolkit is deployed on a remote server using Docker, remove the line `sh $SSH_PROJECT_DIR/.github/scripts/run_src_migration.sh` from the workflow file.
- If using source code, remove `sh $SSH_PROJECT_DIR/.github/scripts/run_docker_migration.sh`.

### Running Migrations on a Remote Database Using Connection Strings
To run migrations on a remote database using connection strings, configure the following secret:
- **`MIGRATION_DATABASE_URL`**: The connection string for your database, formatted as `postgresql+psycopg2://username:password@host:port/database`. For example: 
  ```plaintext
  postgresql+psycopg2://postgres:postgres@db:5432
  ```

If you're using a private database, you may need to establish a VPN or SSH tunnel for access.

### Running Migrations Using Cohere Toolkit's API Migrations Endpoint
For migrations using the Cohere Toolkit's API migrations endpoint, set up these secrets:
- **`MIGRATION_API_ENDPOINT`**: The URL for the Cohere Toolkit API migrations endpoint, formatted as `https://<Your Cohere Toolkit hostname>:<API port, 8000 by default>/migrate`.
- **`MIGRATION_API_TOKEN`**: The API token for authentication with the Cohere Toolkit API migrations endpoint, retrievable from the Toolkit's `.env` file.

### Default Migration Behavior
- If all the required secrets are configured, the action will default to the remote database migrations type.
- If certain variables are not set, the migration type will be determined based on the available variables.
- If the script cannot identify a migration type (due to unset variables), it will exit with an error message.
