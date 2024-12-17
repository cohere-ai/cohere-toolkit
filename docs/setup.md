### Building and Running Locally

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. **Install Poetry and Docker**:
   Install [Poetry >= 1.7.1](https://python-poetry.org/docs/#installation)
   Install [Docker](https://www.docker.com/products/docker-desktop/)
   Install [Docker Compose >= 2.22](https://docs.docker.com/compose/install/)

3. **Set Up with Make**:
   Run:
   ```bash
   make first-run
   ```
   This generates the necessary configuration files and applies database migrations.

4. **Manual Configuration**:
   If you prefer:
   - Create a `configuration.yaml` file based on `configuration.template.yaml`.
   - Replace the placeholders with your actual values.

### Environment Setup for Windows/MacOS

- **Windows**: Follow the detailed setup provided for PowerShell and conda environment.
- **MacOS**: Ensure you have Xcode, Homebrew, and follow the steps to create the virtual environment.

### Environment Variables

Ensure your `configuration.yaml` and `secrets.yaml` file are properly generated and have valid values, especially for the following: 

- `cohere_platform.api_key` (in the secrets file): Your API key for Cohere.
- `database.url` (in the config file): Connection string for PostgreSQL.
- `redis.url` (in the config file): Connection string for Redis.

### Local Database Setup

1. **Migrate the Database**:
   After setting up, run:
   ```bash
   make migrate
   ```

2. **Resetting the Database**:
   If needed, reset and migrate again:
   ```bash
   make reset-db
   make migrate
   ```

### Testing and Development

1. **Install Development Dependencies**:
   ```bash
   make install
   ```

2. **Run Tests**:
   Spin up the test DB and run tests:
   ```bash
   make test-db
   make run-tests
   ```

3. **Database Model Changes**:
   To make changes to the database models:
   - Create a migration with:
     ```bash
     make migration message="Your migration message"
     ```
   - Then migrate:
     ```bash
     make migrate
     ```

### Additional Tips

- **Linting and Formatting**: Use `make lint` and `make lint-fix` for maintaining code quality.
- **VSCode Setup**: Install extensions for Ruff and set up your environment as per the provided recommendations.
