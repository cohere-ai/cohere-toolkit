# Github Actions for Automated DB Migrations

This guide will help you set up a Github Action to automatically run database migrations when you push changes to your repository.

## Prerequisites
To set up the Github Action, you will need to have the following:
    - access with admin permissions to the repository you want to set up the action for
    - a database that you want to run migrations on

## Steps
This guide will walk you through the steps to set up the Github Action for automated database migrations.
We will provide several types of migrations execution, including:
    - running migrations using SSH access to a remote server
    - running migrations on a remote database using connection strings
    - running migrations on a remote database using Cohere Toolkit's API migrations endpoint
For each type of migration execution we need to setup Github environment and secrets.
To seting up the Github environment and secrets, follow the steps below:
- navigate to your repository on Github
- click on the `Settings` tab
- click on the `Environments` menu on the left
- click on the `New environment` button or select an existing environment(we will use the `Production` environment in this guide)
- fill in the environment name and click on the `Configure environment` button
- optionally set rules for the environment, for example, you can set the `Production` environment to be available only for the `main` branch
- click on the `Add secret` button

### Running Migrations using SSH access to a remote server
To run migrations using SSH access to a remote server, you will need to set up the following secrets
- `SSH_PRIVATE_KEY` - the private key to use for SSH authentication
- `SSH_HOST` - the hostname or IP address of the remote server
- `SSH_PORT` - the port to use for SSH authentication
- `SSH_USER_NAME` - the username to use for SSH authentication
The sample Github Action workflow file is located at `.github/workflows/run_alembic_migrations.yml`
Set the `SSH_PROJECT_DIR` variable to the path to the project directory on the remote server. See comments in the `run_alembic_migrations.yml` file for more details.
The action scripts are located at `.github/scripts` directory. The `run_docker_migration.sh` script is used
to run the migrations using Docker. The `run_src_migration.sh` script is used to run the migrations using the source code.
If the Toolkit is deployed on a remote server using Docker, please remove `sh $SSH_PROJECT_DIR/.github/scripts/run_src_migration.sh` string from the `run_alembic_migrations.yml`
If the Toolkit is deployed on a remote server using the source code, please remove `sh $SSH_PROJECT_DIR/.github/scripts/run_docker_migration.sh` string from the `run_alembic_migrations.yml`
Please note that this is a basic example and you may need to adjust the scripts to fit your specific use case.

### Running Migrations on a remote database using connection strings
To run migrations on a remote database using connection strings, you will need to set up the following secrets
In this example, we will use a PostgreSQL database available from the internet. If you are using a private database, you may need to set up a VPN or SSH tunnel to access the database.
- `MIGRATION_DATABASE_URL` - the connection string to the database. It should be in the format `postgresql+psycopg2://username:password@host:port/database` eg. `postgresql+psycopg2://postgres:postgres@db:5432`

### Running Migrations on a remote database using Cohere Toolkit's API migrations endpoint
To run migrations on a remote database using Cohere Toolkit's API migrations endpoint, you will need to set up the following secrets
- `MIGRATION_API_ENDPOINT` - the URL of the Cohere Toolkit API migrations endpoint, eg. `https://>Your Cohere Toolkit host name<:>API port, 8000 by default</migrate`
- `MIGRATION_API_TOKEN` - the API token to use for authentication with the Cohere Toolkit API migrations endpoint. You can get the API token from the Toolkit's `.env` file

Please note that this is a basic example and you may need to adjust the scripts to fit your specific use case.
If all the secrets above are set up, the remote database migrations type will used as default.
If some variables are not set, the migration type will be selected based on the set variables.
If script cant select the migration type(some variables are not set), the script will exit with an error message.
