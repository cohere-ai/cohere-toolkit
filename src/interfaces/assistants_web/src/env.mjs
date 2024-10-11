/* eslint-disable no-process-env */
import { createEnv } from '@t3-oss/env-nextjs';
import {
  useCohereClient,
} from '@/cohere-client';
import z from 'zod';

const checkBackendHealth = async () => {
  const cohereClient = useCohereClient();
  const health = await cohereClient.getHealth();

  console.log("Checking health")
  console.log(health)

  if (response.ok) {
    console.log('Backend is healthy.');
    return true;
  } else {
    console.error('Backend health check failed.');
    throw new Error('Backend health check failed. Please ensure the backend is running properly.');
  }
};

const readVariable = (key) => {
  if (typeof window === 'undefined') return process.env[key];
  return window.__ENV[key];
};

async function setupEnv() {
  await checkBackendHealth();

  return createEnv({
    server: {
      API_HOSTNAME: z.string().default('http://backend:8000'),
    },
    client: {
      NEXT_PUBLIC_API_HOSTNAME: z.string().default('http://localhost:8000'),
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
      NEXT_PUBLIC_API_HOSTNAME: readVariable('NEXT_PUBLIC_API_HOSTNAME'),
      NEXT_PUBLIC_FRONTEND_HOSTNAME: readVariable('NEXT_PUBLIC_FRONTEND_HOSTNAME'),
      NEXT_PUBLIC_GOOGLE_DRIVE_CLIENT_ID: readVariable('NEXT_PUBLIC_GOOGLE_DRIVE_CLIENT_ID'),
      NEXT_PUBLIC_GOOGLE_DRIVE_DEVELOPER_KEY: readVariable('NEXT_PUBLIC_GOOGLE_DRIVE_DEVELOPER_KEY'),
      NEXT_PUBLIC_HAS_CUSTOM_LOGO: readVariable('NEXT_PUBLIC_HAS_CUSTOM_LOGO'),
    },
    emptyStringAsUndefined: true,
    skipValidation: ['lint', 'format', 'test', 'test:coverage', 'test:watch', 'build'].includes(
      process.env.npm_lifecycle_event
    ),
  });
};

// Export the environment setup as a promise that resolves when the health check is done
export const env = await setupEnv();