import { HydrationBoundary, QueryClient, dehydrate } from '@tanstack/react-query';
import { NextPage } from 'next';
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

import { LeftPanel } from '@/components/Agents/LeftPanel';
import { HotKeys } from '@/components/Shared/HotKeys';
import { Swipeable } from '@/components/Swipeable';
import { COOKIE_KEYS, DEFAULT_AGENT_TOOLS } from '@/constants';
import { getCohereServerClient } from '@/server/cohereServerClient';

const MainLayout: NextPage<React.PropsWithChildren> = async ({ children }) => {
  const cohereServerClient = getCohereServerClient();
  const strategies = await cohereServerClient.getAuthStrategies();
  if (strategies.length !== 0) {
    const cookieStore = cookies();
    const authToken = cookieStore.get(COOKIE_KEYS.authToken);

    if (!authToken) {
      return redirect('/login');
    }
  }

  const queryClient = new QueryClient();

  await Promise.all([
    queryClient.prefetchQuery({
      queryKey: ['listAgents'],
      queryFn: async () => {
        const agents = await cohereServerClient.listAgents({});
        return agents;
      },
    }),
    queryClient.prefetchQuery({
      queryKey: ['tools'],
      queryFn: async () => {
        const tools = await cohereServerClient.listTools({});
        return tools.filter((tool) => !DEFAULT_AGENT_TOOLS.includes(tool.name ?? ''));
      },
    }),
  ]);

  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <div className="flex h-screen w-full flex-1 flex-col gap-3 bg-mushroom-900 p-3 dark:bg-volcanic-60">
        <div className="relative flex h-full flex-grow flex-col flex-nowrap gap-3 overflow-hidden lg:flex-row">
          <LeftPanel />
          <section className="relative flex h-full min-w-0 flex-grow flex-col overflow-hidden">
            <HotKeys />
            <Swipeable />
            {children}
          </section>
        </div>
      </div>
      <LeftPanel className="rounded-bl-none rounded-tl-none md:hidden" />
    </HydrationBoundary>
  );
};

export default MainLayout;
