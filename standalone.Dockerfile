FROM ghcr.io/cohere-ai/terrarium:latest as terrarium

FROM python:3.11-buster
LABEL authors="Cohere"
## set ENV for python
ENV PYTHON_VERSION=3.11.8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8
ENV LANG C.UTF-8
ENV PYTHONPATH=/workspace/src/
# "Activate" the venv manually for the context of the container
ENV VIRTUAL_ENV=/workspace/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Keep the poetry venv name and location predictable
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

#install Sqlite3 > 3.35 for Chroma DB
RUN cd /usr/src \
    && wget https://www.sqlite.org/2024/sqlite-autoconf-3450300.tar.gz \
    && tar zxvf sqlite-autoconf-3450300.tar.gz \
    && cd sqlite-autoconf-3450300 \
    && ./configure \
    && make \
    && make install \
    && rm -rf /usr/src/sqlite-autoconf-3450300.tar.gz /usr/src/sqlite-autoconf-3450300

# Install poetry
RUN pip3 install --no-cache-dir poetry==1.6.1

WORKDIR /workspace

# Copy dependency files to avoid cache invalidations
COPY pyproject.toml poetry.lock README.md ./

# Install dependencies
RUN poetry install

# Copy the rest of the code
COPY src/backend src/backend

# Install PostgreSQL
ENV PG_APP_HOME="/etc/docker-postgresql" \
    PG_VERSION=14 \
    PG_USER=postgres \
    PG_HOME=/var/lib/postgresql \
    PG_RUNDIR=/run/postgresql \
    PG_LOGDIR=/var/log/postgresql \
    PG_CERTDIR=/etc/postgresql/certs \
    PG_TRUST_LOCALNET=true \
    DB_USER=postgre \
    DB_PASS=postgre \
    DB_NAME=toolkit

ENV PG_BINDIR=/usr/lib/postgresql/${PG_VERSION}/bin \
    PG_DATADIR=${PG_HOME}/${PG_VERSION}/main

RUN set -ex \
    && curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && echo "deb http://apt.postgresql.org/pub/repos/apt/ buster-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && apt-get update -y \
    && apt-get install -f -y acl sudo locales \
      postgresql-${PG_VERSION} postgresql-client-${PG_VERSION} postgresql-contrib-${PG_VERSION} \
    && update-locale LANG=C.UTF-8 LC_MESSAGES=POSIX \
    && locale-gen en_US.UTF-8 \
    && DEBIAN_FRONTEND=noninteractive dpkg-reconfigure locales \
    && ln -sf ${PG_DATADIR}/postgresql.conf /etc/postgresql/${PG_VERSION}/main/postgresql.conf \
    && ln -sf ${PG_DATADIR}/pg_hba.conf /etc/postgresql/${PG_VERSION}/main/pg_hba.conf \
    && ln -sf ${PG_DATADIR}/pg_ident.conf /etc/postgresql/${PG_VERSION}/main/pg_ident.conf \
    && rm -rf ${PG_HOME} \
    && rm -rf /var/lib/apt/lists/*

COPY docker_scripts/ ${PG_APP_HOME}/
COPY docker_scripts/entrypoint.sh /sbin/entrypoint.sh
RUN chmod 755 /sbin/entrypoint.sh \
# Install nodejs
    && curl -sL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g pnpm \
# pm2 to start frontend
    &&  npm install -g pm2

# ENV for frontend


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

RUN npm install

# Terrarium
WORKDIR /usr/src/app
RUN npm install -g ts-node
COPY --from=terrarium /usr/src/app/package*.json ./
RUN npm install \
    && npm prune --production
COPY --from=terrarium /usr/src/app/. .
ENV ENV_RUN_AS "docker"

# Ports to expose
EXPOSE 5432/tcp
EXPOSE 8000/tcp
EXPOSE 4000/tcp
EXPOSE 8080/tcp
WORKDIR ${PG_HOME}

CMD ["/sbin/entrypoint.sh"]
