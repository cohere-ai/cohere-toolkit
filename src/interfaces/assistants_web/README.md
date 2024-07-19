# Assistants Chat Interface

Cohere's open source web interface for users to have helpful conversations with our conversational models.

> [!CAUTION]
> This is a work in progress interface that will replace coral_web, for now refer to (coral_web)[../coral_web/README.md].

## Usage

```shell
# start in development mode
npm dev

# build for production
npm build

# start in production mode
npm start

# lint
npm lint
```

## Environment Variables

We define environment-specific variables in the `.env.<<ENVIRONMENT>>` files and our current supported environments are: `production`, `stg`/`staging`, `ci`, and `development`. The following are our supported variables:

| Variable                      | Description                                                 |
| ----------------------------- | ----------------------------------------------------------- |
| NEXT_PUBLIC_API_HOSTNAME      | API hostname that indicates the backend environment to hit. |
| NEXT_PUBLIC_FRONTEND_HOSTNAME | The host for the web interface.                             |
