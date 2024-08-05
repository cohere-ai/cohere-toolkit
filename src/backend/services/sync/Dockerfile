FROM python:3.11

RUN apt-get update && apt-get -y install cron vim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PYTHONIOENCODING=utf-8

WORKDIR /app

RUN pip install poetry==1.6.1
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache
COPY ./pyproject.toml ./poetry.lock ./
RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --no-root

COPY ./src/backend/services/sync/crontab /etc/cron.d/crontab
COPY ./src/backend /app/src/backend

RUN chmod 0644 /etc/cron.d/crontab
RUN /usr/bin/crontab /etc/cron.d/crontab
RUN touch /etc/cron.log
RUN chmod +x /app/src/backend/services/sync/publisher.sh

# run crond as main process of container
CMD ["cron", "-f"]