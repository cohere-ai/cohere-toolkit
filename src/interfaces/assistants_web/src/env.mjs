/* eslint-disable no-process-env */
import { createEnv } from '@t3-oss/env-nextjs';
import z from 'zod';

export const env = createEnv({
  server: {
    API_HOSTNAME: z.string().default('http://backend:8000'),
  },
  client: {
    NEXT_PUBLIC_API_HOSTNAME: z.string(),
    NEXT_PUBLIC_FRONTEND_HOSTNAME: z.string().optional().default('http://localhost:4000'),
    NEXT_PUBLIC_GOOGLE_DRIVE_CLIENT_ID: z.string().optional(),
    NEXT_PUBLIC_GOOGLE_DRIVE_DEVELOPER_KEY: z.string().optional(),
    NEXT_PUBLIC_HAS_CUSTOM_LOGO: z
      .string()
      .optional()
      .default('false')
      .refine((s) => s === 'true' || s === 'false')
      .transform((s) => s === 'true'),
  },
  runtimeEnv: {
    API_HOSTNAME: process.env.API_HOSTNAME,
    NEXT_PUBLIC_API_HOSTNAME: process.env.NEXT_PUBLIC_API_HOSTNAME,
    NEXT_PUBLIC_FRONTEND_HOSTNAME: process.env.NEXT_PUBLIC_FRONTEND_HOSTNAME,
    NEXT_PUBLIC_GOOGLE_DRIVE_CLIENT_ID: process.env.NEXT_PUBLIC_GOOGLE_DRIVE_CLIENT_ID,
    NEXT_PUBLIC_GOOGLE_DRIVE_DEVELOPER_KEY: process.env.NEXT_PUBLIC_GOOGLE_DRIVE_DEVELOPER_KEY,
    NEXT_PUBLIC_HAS_CUSTOM_LOGO: process.env.NEXT_PUBLIC_HAS_CUSTOM_LOGO,
  },
  emptyStringAsUndefined: true,
  skipValidation: ['lint', 'format', 'test', 'test:coverage', 'test:watch'].includes(
    process.env.npm_lifecycle_event
  ),
});
