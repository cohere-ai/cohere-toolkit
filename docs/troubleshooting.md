### General Troubleshooting Steps

- **Ensure Latest Release:** 
  Always start with the latest release from the [Cohere toolkit releases](https://github.com/cohere-ai/cohere-toolkit/releases) or the latest commit on the main branch.

### Common Issues

1. **Community Features Not Accessible:**
   - Add `USE_COMMUNITY_FEATURES=True` to your `.env` file.

2. **Multiple Errors After Running `make dev` for the First Time:**
   - Run `make migrate` before executing `make dev`.

3. **Error Installing `psycopg2`:**
   - If you encounter an error related to PEP 517 builds, replace `psycopg2` with `psycopg2-binary` in `pyproject.toml`.

4. **`pg_config` Executable Not Found:**
   - Ensure PostgreSQL is installed properly. For MacOS, use:
     ```bash
     brew install postgresql
     ```
   - Check [PostgreSQL documentation](https://www.postgresql.org/download/) for other OS instructions.

5. **Platform Mismatch Error:**
   - Add the following to your `docker_compose.yml`:
     ```yaml
     terrarium:
       platform: linux/amd64
       image: ghcr.io/cohere-ai/terrarium:latest
       ports:
         - '8080:8080'
       expose:
         - '8080'
     ```

6. **Debugging Locally:**
   - Run `make dev` to start the Docker containers with reloading enabled.
   - In a separate shell, execute `make attach` to attach an interactive shell for debugging.
   - Use `import pdb; pdb.set_trace()` in your code for debugging.

7. **Alembic Migrations Out of Sync Error:**
   - If migrations diverge due to changes in different branches:
     - Downgrade your local branch:
       ```bash
       docker compose run --build backend alembic -c src/backend/alembic.ini downgrade -1
       ```
     - Delete the out-of-sync migration file (e.g., `<my_migration_id>.py`).
     - Run `make migrate` to sync with the main branch.
     - Regenerate your migrations:
       ```bash
       make migration message="Your migration changes"
       ```
