# Command Slack Bot

This is a Slack bot that uses the Cohere Toolkit to generate responses to messages.

## Usage

```shell
# start in development mode
pnpm dev

# build for production
pnpm build

# run sql migrations and start in production mode
pnpm start

# lint
pnpm lint

# check formatting with prettier
pnpm format

# format with prettier
pnpm format:write

# run all unit tests, with coverage report
pnpm test

# run and watch unit tests
pnpm test:watch
```

## Project Structure

```text
slack_bot/
├─ src/
│  ├─ constants.ts
│  ├─ api/
│  │   ∟ functions that interact with the cohere api live here
│  ├─ handlers/
│  │   ∟ functions that handle slack events live here
│  ├─ utils/
│  │   ∟ miscellaneous utility functions live here
```

## Socket Mode and HTTP Mode

The Slack bot supports two modes of operation: Socket Mode and HTTP Mode.

In Socket Mode, the application initiates a connection to Slack via a long-lived TCP connection. This mode is recommended for local development and for private cloud deployment, since it requires no public HTTP endpoints to be exposed.

In HTTP Mode, the application exposes HTTP endpoints that Slack can use to send events and commands. This mode is recommended for public cloud deployment, since it supports installation via the public [Slack App Directory](https://api.slack.com/start/distributing#app_directory_apps).

The `SLACK_CONNECTION_MODE` environment variable controls which mode is used. Additional environment variables are required for each mode, as described under [Environment variables](#environment-variables).

Socket mode must also enabled in the Slack app configuration, under "Socket Mode" in the Settings menu.

The event subscription request URL will be https://slack-bot-host/slack/events, where "slack-bot-host" should be replaced with the hostname where the command slack bot is deployed.

See also:

- https://api.slack.com/apis/connections/socket
- https://slack.dev/bolt-js/concepts#socket-mode

## Database setup

The Command Slack bot requires a PostgreSQL database instance. Once you have PostgreSQL running, the following steps can be used to create a database for the Command Slack bot. These steps are a guide for local development.

Create a database named `commandslackdb` with user `commandslack` and password `password` (with the `CREATEDB` privilege for [Prisma Migrate](https://www.prisma.io/docs/concepts/components/prisma-migrate/shadow-database) in development only). You can do this with the following commands:

```shell
psql --host=localhost --port=5432 --username=postgres
```

Then, in the psql shell:

```
CREATE DATABASE commandslackdb;
CREATE USER commandslack WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE commandslackdb TO commandslack;
ALTER USER commandslack WITH CREATEDB;
```

For production use, configure PostgreSQL appropriately and set the `DATABASE_URL` variable in the environment or `.env` file.

## Database migrations

Apply migrations in development:

```
./node_modules/.bin/prisma migrate dev
```

Create new migration:

```
./node_modules/.bin/prisma migrate dev --name <name-of-migration>
```

Apply migrations in production:

```
./node_modules/.bin/prisma migrate deploy
```

_Note: `prisma migrate deploy` is run automatically upon `pnpm start` in production._

See also:

- https://www.prisma.io/docs/concepts/components/prisma-migrate/migrate-development-production

## Slack App Configuration

To use the bot with Slack, you'll need to create a new Slack App and install it to your workspace. The easiest way to do this is to use
the option to create a new app **from an app manifest**. Use the `example-manifest.yaml` file in this repo and tweak as needed. Ensure
that you change the toolkit host in the URLs to the URL where the Slack bot is being hosted.

To create a new Slack app, visit:

https://api.slack.com/apps?new_app=1

Alternatively, you can create a new Slack app from scratch. You can do this by following the instructions in the [Slack Bolt documentation](https://slack.dev/bolt-js/tutorial/getting-started), including the "Tokens and installing apps" step and "Setting up events" step.

As a result of this process, you should have a signing secret, bot token, and app-level token, which you must set as environment variables.

There are several differences in the Slack app configuration based on whether you use socket mode or HTTP mode.

### Socket Mode

You must enable socket mode in the Slack app configuration.

See: https://slack.dev/bolt-js/tutorial/getting-started#setting-up-events.

### HTTP Mode

With HTTP mode, you must ensure that event subscriptions are enabled on the _Event Subscriptions_ page under the _Features_ menu. You must also ensure that the URL to the Command Slack bot's events hook has been entered into the _Request URL_ field. The URL to handle events should be https://slack-bot-host/slack/events.

With HTTP mode it is also necessary to grant OAuth permissions.

### Testing with HTTP Mode

To test with HTTP Mode, you'll need to expose the bot to the public internet. You can do this with [ngrok](https://ngrok.com/):

```shell
brew install ngrok
ngrok http 3000
```

This command will expose a public HTTPS server which you can use to receive Slack events, e.g. https://6c36-142-181-59-160.ngrok-free.app. Use this URL in your App's config on https://api.slack.com/apps.

You can install the Slack App to a workspace by appending `/slack/install`, e.g. https://6c36-142-181-59-160.ngrok-free.app/slack/install.

For some ngrok features, you will need to sign up with a free account: https://ngrok.com/signup.

## Environment variables

| Variable                 | Required for Socket Mode | Required for HTTP Mode | Example                                                            | Description                                                                                                                    |
| ------------------------ | ------------------------ | ---------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| `TOOLKIT_API_HOST`       | Yes                      | Yes                    | `http://0.0.0.0:8000`                                              | Protocol and host to access the Cohere Toolkit API.                                                                            |
| `COHERE_SLACK_TEAM_ID`   | Yes                      | Yes                    | `TV82C32HX`                                                        | Cohere's Slack Workspace Team ID. Can include multiple comma separated IDs                                                     |
| `COHERE_ORGANIZATION_ID` | Yes                      | Yes                    | `d489c39a-e152-49da-9ddc-9801bd74d823`                             | Cohere's Org ID                                                                                                                |
| `COHERE_LOCAL_API_KEY`   | No                       | No                     | `abc123`                                                           | API key used for local development when running in socket mode. Can be set through the `/setup-command` command.               |
| `SLACK_CONNECTION_MODE`  | Yes                      | Yes                    | `socket` or `http`                                                 | Whether to use Socket Mode or HTTP Mode.                                                                                       |
| `SLACK_SIGNING_SECRET`   | Yes                      | Yes                    | `abc123`                                                           | Signing secret from _Basic Information -> App Credentials -> Signing Secret_.                                                  |
| `SLACK_BOT_TOKEN`        | Yes                      | No                     | `xoxb-abc123`                                                      | OAuth token from _OAuth & Permissions -> Bot User OAuth Token_.                                                                |
| `SLACK_APP_TOKEN`        | Yes                      | No                     | `xapp-abc123`                                                      | App-Level token from _Basic Information -> App-Level Tokens_. Must contain the `connections:write` scope.                      |
| `DATABASE_URL`           | No                       | Yes                    | `postgresql://commandslack:password@localhost:5432/commandslackdb` | Prisma-compatible PostgreSQL database URL.                                                                                     |
| `SLACK_CLIENT_ID`        | No                       | Yes                    | `abc.123`                                                          | OAuth client ID from _Basic Information -> App Credentials -> Client ID_.                                                      |
| `SLACK_CLIENT_SECRET`    | No                       | Yes                    | `abc123`                                                           | OAuth client secret from _Basic Information -> App Credentials -> Client Secret_.                                              |
| `SLACK_STATE_SECRET`     | No                       | Yes                    | `my-state-secret`                                                  | Sufficiently random static string used to secure the OAuth flow in web browsers. This can be changed when redeploying the app. |
| `SLACK_INSTALL_PASSWORD` | No                       | Yes                    | `mypassword`                                                       | A value to make the installation URL hard to guess. The URL will be `${HOST}/slack/install/${SLACK_INSTALL_PASSWORD}`.         |
| `COMMAND_SUFFIX`         | Yes                      | Yes                    | `-stg`                                                             | Suffix to add to command names to avoid collisions                                                                             |
| `SENTRY_DSN`             | No                       | No                     | `https://{SENTRY-ACCOUNT}.ingest.sentry.io/{SENTRY-ID}`            | Optional value to send error events to the right Sentry project                                                                |

In development with `pnpm dev`, the bot will automatically load environment variables from a `.env` file in the root of the project. You can copy the `.env.example` file to get started:

```shell
cp .env.example .env
# edit .env with values from your Slack App
```

## Resources

- https://slack.dev/bolt-js/tutorial/getting-started
- https://slack.dev/bolt-js/reference
- https://github.com/vercel/turbo/tree/main/examples/kitchen-sink/apps/api
- https://github.com/slackapi/bolt-js/tree/main/examples/getting-started-typescript
