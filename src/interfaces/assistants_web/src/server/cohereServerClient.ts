import fetch from 'cross-fetch';
import { cookies } from 'next/headers';

import { CohereClient, Fetch } from '@/cohere-client';
import { COOKIE_KEYS } from '@/constants';
import { env } from '@/env.mjs';

export const getCohereServerClient = () => {
  const cookieStore = cookies();
  const token = cookieStore.get(COOKIE_KEYS.authToken);
  const apiFetch: Fetch = async (resource, config) => await fetch(resource, config);
  return new CohereClient({
    hostname: env.API_HOSTNAME,
    fetch: apiFetch,
    authToken: token?.value,
  });
};
