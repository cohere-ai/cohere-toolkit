import fetch from 'cross-fetch';
import { NextPage } from 'next';
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

import { MainLayout } from '@/app/(main)/MainLayout';
import { CohereClient, Fetch } from '@/cohere-client';
import { COOKIE_KEYS } from '@/constants';
import { env } from '@/env.mjs';

const makeCohereClient = () => {
  const apiFetch: Fetch = async (resource, config) => await fetch(resource, config);
  return new CohereClient({
    hostname: env.API_HOSTNAME,
    fetch: apiFetch,
  });
};

const Layout: NextPage<React.PropsWithChildren> = async ({ children }) => {
  const cohereClient = makeCohereClient();
  const strategies = await cohereClient.getAuthStrategies();
  if (strategies.length !== 0) {
    const cookieStore = cookies();
    const authToken = cookieStore.get(COOKIE_KEYS.authToken);

    if (!authToken) {
      return redirect('/login');
    }
  }

  return <MainLayout>{children}</MainLayout>;
};

export default Layout;
