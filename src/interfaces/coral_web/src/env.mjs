/* eslint-disable no-process-env */
import { createEnv } from '@t3-oss/env-nextjs';
import z from 'zod';

export const env = createEnv({
  server: {
  },
  client: {
    NEXT_PUBLIC_API_HOSTNAME: z.string(),
    NEXT_PUBLIC_HAS_CUSTOM_LOGO: z.string().optional().default('false'),
  },
  runtimeEnv: {
    NEXT_PUBLIC_API_HOSTNAME: process.env.NEXT_PUBLIC_API_HOSTNAME,
    NEXT_PUBLIC_HAS_CUSTOM_LOGO: process.env.NEXT_PUBLIC_HAS_CUSTOM_LOGO,
  },
  emptyStringAsUndefined: true,
  skipValidation: ['lint', 'format', 'test', 'test:coverage', 'test:watch'].includes(
    process.env.npm_lifecycle_event
  ),
});
