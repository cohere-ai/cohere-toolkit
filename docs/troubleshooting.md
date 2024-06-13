
# Troubleshooting

Ensure you are working off the [latest release](https://github.com/cohere-ai/cohere-toolkit/releases) and/or the latest commit from the main branch.

## Community features are not accessible

Make sure you add `USE_COMMUNITY_FEATURES=True` to your .env file.


##  Multiple errors after running make dev for the first time

Make sure you run the following command before running make dev:

```bash
make migrate
```

##  Error: pg_config executable not found.

Make sure that all requirements including postgres are properly installed.

If you're using MacOS, run:
```bash
brew install postgresql
```

For other operating systems, you can check the [postgres documentation](https://www.postgresql.org/download/).


##  Debugging locally

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


## Alembic migrations out of sync error:

When developing on the backend if database model changes are made in different git branches your Alembic migrations may diverge.

If you have changes on your branch_a that contains a migration <my_migration_id>.py that is out of sync with the main branch, first downgrade your local branch using:

docker compose run --build backend alembic -c src/backend/alembic.ini downgrade -1
Then delete <my_migration_id>.py for your existing changes, and run:

make migrate
To sync with main, then:

make migration
to regenerate your migrations.