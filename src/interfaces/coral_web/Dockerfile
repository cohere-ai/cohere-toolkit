FROM node:20-alpine AS base

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

COPY src ./src
COPY public ./public
COPY next.config.mjs .
COPY tsconfig.json .
COPY tailwind.config.js .
COPY postcss.config.js .
COPY .en[v] .env

# Next.js collects completely anonymous telemetry data about general usage. Learn more here: https://nextjs.org/telemetry
ENV NEXT_TELEMETRY_DISABLED 1

# Note: Don't expose ports here, Compose will handle that for us

# Start Next.js in development mode based on the preferred package manager
CMD npm run dev
