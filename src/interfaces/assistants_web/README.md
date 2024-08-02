# Assistants Chat Interface

Cohere's open source web interface for users to have helpful conversations with our conversational models.

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

| Variable                               | Description                                                                                  |
| -------------------------------------- | -------------------------------------------------------------------------------------------- |
| NEXT_PUBLIC_API_HOSTNAME               | API hostname that indicates the backend environment to hit.                                  |
| NEXT_PUBLIC_FRONTEND_HOSTNAME          | (Optional) The host for the web interface.                                                   |
| NEXT_PUBLIC_HAS_CUSTOM_LOGO            | (Optional) Whether a custom logo should be used. See `docs/theming.md` for more information. |
| NEXT_PUBLIC_GOOGLE_DRIVE_CLIENT_ID     | (Optional) The client ID to enable Google Drive file upload - see Google Picker API docs.    |
| NEXT_PUBLIC_GOOGLE_DRIVE_DEVELOPER_KEY | (Optional) API key to enable Google Drive file upload - see Google Picker API docs.          |
