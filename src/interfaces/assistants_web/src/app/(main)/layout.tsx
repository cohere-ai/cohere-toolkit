import fetch from 'cross-fetch';
import { NextPage } from 'next';
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

import { CohereClient, Fetch } from '@/cohere-client';
import { AgentLeftPanel } from '@/components/Agents/AgentLeftPanel';
import { AgentsList } from '@/components/Agents/AgentsList';
import { COOKIE_KEYS } from '@/constants';
import { env } from '@/env.mjs';
import { cn } from '@/utils';

const makeCohereClient = () => {
  const apiFetch: Fetch = async (resource, config) => await fetch(resource, config);
  return new CohereClient({
    hostname: env.API_HOSTNAME,
    fetch: apiFetch,
  });
};

const MainLayout: NextPage<React.PropsWithChildren> = async ({ children }) => {
  const cohereClient = makeCohereClient();
  const strategies = await cohereClient.getAuthStrategies();
  if (strategies.length !== 0) {
    const cookieStore = cookies();
    const authToken = cookieStore.get(COOKIE_KEYS.authToken);

    if (!authToken) {
      return redirect('/login');
    }
  }

  return (
    <>
      <div className="flex h-screen w-full flex-1 flex-col gap-3 bg-mushroom-900 p-3 dark:bg-volcanic-60">
        <div
          className={cn(
            'relative flex h-full flex-grow flex-col flex-nowrap gap-3 overflow-hidden lg:flex-row'
          )}
        >
          <AgentLeftPanel className="hidden md:flex">
            <AgentsList />
          </AgentLeftPanel>
          <section
            className={cn('relative flex h-full min-w-0 flex-grow flex-col', 'overflow-hidden')}
          >
            {children}
          </section>
        </div>
      </div>
      <AgentLeftPanel className="rounded-bl-none rounded-tl-none md:hidden">
        <AgentsList />
      </AgentLeftPanel>
    </>
  );
};

export default MainLayout;
