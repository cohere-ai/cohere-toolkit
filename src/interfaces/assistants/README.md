# Chat

Cohere's open source web interface for users to have helpful conversations with our conversational models.

## Usage

```shell
# start in development mode
pnpm dev

# build for production
pnpm build

# start in production mode
pnpm start

# lint
pnpm lint
```

## Environment Variables

We define environment-specific variables in the `.env.<<ENVIRONMENT>>` files and our current supported environments are: `production`, `stg`/`staging`, `ci`, and `development`. The following are our supported variables:

| Variable                      | Description                                                 |
| ----------------------------- | ----------------------------------------------------------- |
| NEXT_PUBLIC_API_HOSTNAME      | API hostname that indicates the backend environment to hit. |
| NEXT_PUBLIC_FRONTEND_HOSTNAME | The host for the web interface.                             |

### Resources

- https://testing-library.com/docs/react-testing-library/intro/
- https://kentcdodds.com/blog/common-mistakes-with-react-testing-library
