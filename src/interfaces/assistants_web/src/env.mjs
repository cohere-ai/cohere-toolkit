/* eslint-disable no-process-env */
import { createEnv } from '@t3-oss/env-nextjs';
import z from 'zod';

const checkBackendHealth = async () => {
  const url = process.env.API_HOSTNAME || 'http://backend:8000';

  try {
    const response = await fetch(`${url}/health`);
    if (response.ok) {
      console.log('Backend is healthy, business as usual.');
    } else {
      throw new Error('Backend health check failed, make sure your backend server is running correctly.');
    }
  } catch (error) {
    console.error('Backend is unreachable:', error.message);
    throw new Error('Backend is unreachable. Make sure your backend server is running correctly.');
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