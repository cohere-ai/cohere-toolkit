FROM python:3.11

# Keeps Python from generating .pyc files in the container
# Turns off buffering for easier container logging
# Force UTF8 encoding for funky character handling
# Needed so imports function properly
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8
ENV PYTHONPATH=/workspace/src/
ENV PYDEVD_DISABLE_FILE_VALIDATION=1
# Keep the venv name and location predictable
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

# "Activate" the venv manually for the context of the container
ENV VIRTUAL_ENV=/workspace/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /workspace

# Need to expose port in ENV to use in CMD
ARG PORT=8000
ENV PORT=${PORT}

# Build with community packages
ARG INSTALL_COMMUNITY_DEPS
ARG DEBUGGER_IDE
ENV DEBUGGER_IDE=${DEBUGGER_IDE}
# Copy dependency files to avoid cache invalidations
COPY pyproject.toml poetry.lock ./
COPY docker_scripts/debugrun-entrypoint.sh ./debugrun-entrypoint.sh
RUN ["chmod", "+x", "./debugrun-entrypoint.sh"]

# Install poetry
RUN pip install --no-cache-dir poetry==1.8.4
# Conditional installation of dependencies
RUN if [ "$INSTALL_COMMUNITY_DEPS" = "true" ]; then \
      if [ "$DEBUGGER_IDE" = "vscode" ]; then \
        poetry install --with dev,community,local-debug; \
      else \
        poetry install --with dev,community; \
      fi; \
    else \
      if [ "$DEBUGGER_IDE" = "vscode" ]; then \
        poetry install --with dev,local-debug; \
      else \
        poetry install --with dev; \
      fi; \
    fi

COPY src/backend/ src/backend/
COPY src/community src/community/

# Copy environment variables optionally 
# IMPORTANT: Can't be put in the docker-compose, will break tests
COPY .en[v] .env

EXPOSE ${PORT}
EXPOSE 5678


CMD  ["/workspace/debugrun-entrypoint.sh"]