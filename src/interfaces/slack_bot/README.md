# Command Slack Bot

This is a Slack bot that uses the Cohere Toolkit to generate responses to messages.

## Getting Started

The Slack bot interface is a Node project that runs independently of the main Toolkit backend. The following steps are required to get up and running with the Slack bot:

- Ensure that you have an instance of the Toolkit running and configured with required secrets
- Ensure that the Slack bot app is accessible from a public ip address
- Create a PostreSQL database and run the Prisma database migrations
- Create a new Slack app in your Slack account based on the example app manifest
- Configure environment variables and generate required values on the Slack website
- Add the Slack app to your workspace and complete OAuth flow
- Run the setup command in your Slack workspace
- Invite Command Slack Bot to a channel
- Optionally set channel parameters to override default model settings
- Begin chatting!

The sections below will provide further details on these required steps.

### Set up the Toolkit

The Slack bot makes use of the Toolkit, and requires the Toolkit to be running separately
from the Slack bot. All requests to the models are made through requests to the Toolkit APIs.

Please see the documentation for the Toolkit to see how configure and deploy it.

https://github.com/cohere-ai/cohere-toolkit

If you are running the Toolkit on localhost, the default API URL should work. If you have
the Toolkit deployed on a server, then you will need to set the `TOOLKIT_API_HOST` environment
variable with the appropriate value.

### Deploy app or configure ngrok for local dev

There are two ways for the Slack bot to receive data from Slack. The recommended way is to use
webhooks, which requires Slack to be able to make HTTP requests to the running Slack bot app from
this repo. For Slack to make those requests, it requires the app to be accessible on a public IP address.
The URLs for the webhooks must be configured in the app manifest on the Slack website.

If the app is deployed to a server, this should be no problem. Use the hostname of the server where
you have deployed it. For local development, however, Slack needs to be able to access the webhook
endpoints running in your local environment, which requires a proxy for local development.

One way of doing this is with a program called ngrok. It is a service that allows you to access code
running on your local machine from a public ip and domain. It is a commercial app, but there is
a free tier that should be sufficient for local development of this app.

Please see https://ngrok.com for instructions on installing ngrok and obtaining an API key.

Once ngrok is set up, you can start it with:

`ngrok http 3000`

On the free plan this will give you a random domain each time. There is a `-domain` option that will
allow you to choose a specific hostname if it is available. Paid accounts can reserve specific
hostnames for your use only, which could be useful for ongoing development, since the hostname needs
to be saved in several different places in the app manifest, and not using a reserved domain could
require you to have to make changes to the app configuration on the Slack website, each time the
ngrok domain you are assigned changes.

Alternatively, the Slack bot can be used with socket mode. With socket mode, the bot will
establish a websocket connection to Slack, over which the Slack events can be received. Socket
mode can simplify local development by eliminating the requirement for a proxy to your local environment.

Use of socket mode requires socket mode to be enabled in the Slack app configuration on the Slack
website, in addition to being enabled and configured with socket mode specific secrets in the
environment variables. See the section further below for more information on configuring socket mode.

### Create PostgreSQL database and run migrations

The Slack bot requires a PostgreSQL database for storing workspace and channel settings. Follow standard
procedures for creating a PostgreSQL database and once the database and PostgreSQL user have been
created, set the `DATABASE_URL` environment variable.

You can use any database name, user and host as long as the `DATABASE_URL` is configured. The following
steps are a guide for how to do this.

Start the psql shell with a postgres admin account.

```shell
psql --host=localhost --port=5432 --username=postgres
```

In the psql shell run the following commands:

```
CREATE DATABASE commandslackdb;
CREATE USER commandslack WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE commandslackdb TO commandslack;
ALTER USER commandslack WITH CREATEDB;
```

Set the `DATABASE_URL` with the db name, user and password you used above:

```shell
DATABASE_URL="postgresql://commandslack:password@localhost:5432/commandslackdb"`
```

Once the database has been set up, you must run the Prisma migrations. In development use:

```shell
prisma migrate dev
```

### Create Slack app

To use the Slack bot, you must create your own app on the api.slack.com website. Choose the option
to create a new app, and choose the option "From an app manifest". Follow the instructions to
choose the workspace, and when prompted for the manifest, choose the YAML option, and copy and paste
the contents of the `example-manifest.yaml` file from this repo.

It is possible to custom configure all the values in Slack, and it is not mandatory to use the
all the settings from the example manifest. For example, you could change the display name
or username of the bot. However, using the `example-manifest.yaml` file will make the process much
simpler. For getting up and running quickly, it is strongly recommended to start with this file,
rather than custom configuring all required values from scratch. There are some important defaults
in the example that could lead to hard to debug problems if they are not present.

When configuring the Slack app, it is important to change the hostnames of all URLs in the example
manifest. Every instance of https://slack-bot-host/slack/events in the example manifest must be
changed to use the domain of your deployed app or the ngrok domain you are using for local development.

### Configure environment variables

For local development, copy the `.env.example` file to `.env`, and edit the values accordingly. The
required values depend on whether you choose to use HTTP mode (recommended for production) or socket mode.

### Add the Slack app to your workspace and complete OAuth flow

The Command Slack bot may appear in your workspace after you create the new app from the manifest, but
it will not work properly without granting permissions with OAuth.

In order for the OAuth flow to work, you must ensure that the Slack app has the redirect URL configured
in the Slack app configuration/manifest. The default redirect URL in the example is set to
https://slack-bot-host/slack/oauth_redirect, but the host name needs to be changed. Ensure this was
done in the previous steps.

To grant OAuth permissions, go to the following URL:

https://slack-bot-host/slack/install/

You can optionally set an environment variable called `SLACK_INSTALL_PASSWORD` to obscure this URL.
If you set the value, the URL to start OAuth flow will be:

https://slack-bot-host/slack/install/password-you-chose

You must of course change the host to the server where the Slack bot is deployed or the proxy address.

This page will redirect you to Slack, and after you grant the permissions, you will be redirected
back to the Slack bot host in your browser. When returning, you should come back to the following
URL:

https://slack-bot-host/slack/oauth_redirect

The above URL does not change based on the value of `SLACK_INSTALL_PASSWORD` like the install
URL does.

When you return, you will be prompted to open the Slack application by your browser. You should allow this.

### Run the setup command in your Slack workspace

The Command Slack bot will add several new `/` commands to your Slack workspace. To begin using the
bot, you must run the `/setup-command` command inside of Slack. If this command is not available in
your workspace, it means that the above steps have not been completed successfully yet.

When the Slack bot is running in production environments, only an administrator of the Slack workspace
can run the `/setup-command` command. When `NODE_ENV` is set to `development`, this restricted is lifted,
and anyone can run `/setup-command`. Some features of the Slack bot may work before this has been run,
but it is advisable to run it as soon as you've completed the OAuth flow, in order to avoid any hard
to debug problems when there is no record in the `WorkspaceSettings` table.

### Invite Command Slack Bot to a channel

If you have followed the above instructions, with the suggested defaults, then you should now have the
Command Slack bot in your workspace. The default username in the example manifest is `@Command`. You
should be able to talk to this user directly, or invite `@Command` to a channel. In order for it to
respond in a channel, you must tag the user `@Command`. Once `@Command` has been tagged in a thread,
it will continue responding to that thread without being tagged.

### Optionally set channel parameters to override default model settings

To see the full list of commands available, type `/command-help` in your workspace in the Slack application.

The configuration commands available include:

- `/set-deployment [deployment name]` - Set the deployment used for a specific channel
- `/view-deployment` - View the deployment used for a specific channel
- `/set-model [model name]` - Set the model used for a specific channel
- `/view-model` - View the model used for a specific channel
- `/set-temperature [0.0 - 5.0]` - Set the temperature used for a specific channel
- `/view-temperature` - View the temperature used for a specific channel
- `/set-preamble [preamble]` - Set the preamble override used for a specific channel
- `/view-preamble` - View the preamble override used for a specific channel
- `/set-tools` - Set tools for a specific channel
- `/view-tools [all]` - View all tools available in your Cohere account or tools enabled for a specific channel

### Begin chatting!

You should now be able to use the Command Slack bot in your workspace. You can communicate with `@Command` via
direct message, or tagging `@Command` in channel messages. There are also several other commands available,
to perform actions such as summarize a thread. To see the full list of things `@Command` can do, run the
`/command-help` command.

## Usage

The Command Slack bot is a Node application built with TypeScript.

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
│  │   ∟ constants live here
│  ├─ cohere-client/
│  │   ∟ functions that interact with the toolkit api live here
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
