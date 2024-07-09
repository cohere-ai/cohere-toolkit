# This Dockerfile is intended for One-Click deployment to Google Cloud Run
# ------------------------------------------------------------------------
FROM ghcr.io/cohere-ai/terrarium:latest as terrarium

FROM python:3.11
LABEL authors="Cohere"
ENV PG_APP_HOME=/etc/docker-app
ENV PYTHON_VERSION=3.11.8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8
ENV LANG C.UTF-8
ENV PYTHONPATH=/workspace/src/
ENV VIRTUAL_ENV=/workspace/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
COPY docker_scripts/gcp-entrypoint.sh /sbin/gcp-entrypoint.sh

RUN chmod 755 /sbin/gcp-entrypoint.sh \
    && curl -sL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get update \
    && apt-get install --no-install-recommends -y nginx nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    && npm install -g pnpm \
    &&  npm install -g pm2

# Copy nginx config \
COPY docker_scripts/nginx.conf /etc/nginx/nginx.conf

WORKDIR /workspace

# Copy dependency files to avoid cache invalidations
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN pip3 install --no-cache-dir poetry==1.6.1 \
    && poetry config installer.max-workers 10 \
    && poetry install \
    && (poetry cache clear --all --no-interaction PyPI || true) \
    && (poetry cache clear --all --no-interaction _default_cache || true)

# Copy the rest of the code
COPY src/backend src/backend
COPY docker_scripts/ ${PG_APP_HOME}/

# Install frontend dependencies
WORKDIR /workspace/src/interfaces/coral_web
COPY src/interfaces/coral_web/src ./src
COPY src/interfaces/coral_web/public ./public
COPY src/interfaces/coral_web/next.config.mjs .
COPY src/interfaces/coral_web/tsconfig.json .
COPY src/interfaces/coral_web/tailwind.config.js .
COPY src/interfaces/coral_web/postcss.config.js .
COPY src/interfaces/coral_web/package.json src/interfaces/coral_web/yarn.lock* src/interfaces/coral_web/package-lock.json* src/interfaces/coral_web/pnpm-lock.yaml* ./
COPY src/interfaces/coral_web/.env.development .
COPY src/interfaces/coral_web/.env.production .

ENV NEXT_PUBLIC_API_HOSTNAME='/api'
RUN npm install \
    && npm run next:build

# Terrarium
WORKDIR /usr/src/app
COPY --from=terrarium /usr/src/app/package*.json ./
RUN npm install -g ts-node \
    && npm install \
    && npm prune --production
COPY --from=terrarium /usr/src/app/. .
ENV ENV_RUN_AS "docker"

# Ports to expose
EXPOSE 4000/tcp
EXPOSE 8000/tcp
EXPOSE 8090/tcp

CMD ["/sbin/gcp-entrypoint.sh"]
