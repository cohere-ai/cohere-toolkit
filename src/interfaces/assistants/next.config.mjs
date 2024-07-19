/**
 * Next.js config utils
 */
import pickBy from 'lodash/pickBy.js';
import { PHASE_PRODUCTION_BUILD, PHASE_PRODUCTION_SERVER } from 'next/constants.js';

import { env } from './src/env.mjs';

/**
 * Get common environment variables used by a Next.js app.
 *
 * @param {Record<string, string>} env - Environment variables, typically `process.env`.
 */
export const getCommonEnvVars = (env) => {
  return {
    ...pickBy(env, (_value, key) => key.startsWith('NEXT_')),
  };
};

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      // Favicons for RAG citations documents
      {
        protocol: 'https',
        hostname: 'www.google.com',
        port: '',
        pathname: '/**',
      },
    ],
  },
  async redirects() {
    return [
      {
        source: '/chat',
        destination: '/',
        permanent: false,
      },
    ];
  },
};

const getNextConfig = (phase) => {
  if (phase === PHASE_PRODUCTION_BUILD || phase === PHASE_PRODUCTION_SERVER) {
    console.info('Next.js environment variables:', getCommonEnvVars(env));
  }
  return nextConfig;
};

export default getNextConfig;
