FROM python:3.11

# Keeps Python from generating .pyc files in the container
# Turns off buffering for easier container logging
# Force UTF8 encoding for funky character handling
# Needed so imports function properly
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8
ENV PYTHONPATH=/workspace/src/
# Keep the venv name and location predictable
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

# "Activate" the venv manually for the context of the container
ENV VIRTUAL_ENV=/workspace/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /workspace

ARG port=8000

# Need to expose port in ENV to use in CMD
ENV PORT=${port}

# Copy dependency files to avoid cache invalidations
COPY pyproject.toml poetry.lock ./

# Install poetry and run poetry install
RUN pip install --no-cache-dir poetry==1.6.1 && \
  poetry install

COPY src/backend/ src/backend/

# Copy environment variables optionally 
# IMPORTANT: Can't be put in the docker-compose, will break tests
COPY .en[v] .env

EXPOSE ${PORT}

CMD uvicorn backend.main:app --reload --host 0.0.0.0 --port ${PORT}
