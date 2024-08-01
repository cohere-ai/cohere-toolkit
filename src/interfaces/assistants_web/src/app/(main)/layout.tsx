import { NextPage } from 'next';
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

import { AgentLeftPanel } from '@/components/Agents/AgentLeftPanel';
import { AgentsList } from '@/components/Agents/AgentsList';
import { MobileHeader } from '@/components/MobileHeader';
import { COOKIE_KEYS } from '@/constants';
import { cn } from '@/utils';

const MainLayout: NextPage<React.PropsWithChildren> = ({ children }) => {
  const cookieStore = cookies();
  const authToken = cookieStore.get(COOKIE_KEYS.authToken);
  if (!authToken) {
    return redirect('/login');
  }

  return (
    <>
      <div className="flex h-screen w-full flex-1 flex-col gap-3 bg-mushroom-900 p-3 dark:bg-volcanic-60">
        <div
          className={cn(
            'relative flex h-full flex-grow flex-col flex-nowrap gap-3 overflow-hidden lg:flex-row'
          )}
        >
          <MobileHeader />
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
