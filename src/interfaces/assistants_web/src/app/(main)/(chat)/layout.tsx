'use client';

import { Transition } from '@headlessui/react';
import { useEffect } from 'react';

import RightPanel from '@/components/Agents/RightPanel';
import { useIsDesktop } from '@/hooks/breakpoint';
import { useListAllDeployments } from '@/hooks/deployments';
import { useConversationStore, useParamsStore, useSettingsStore } from '@/stores';
import { cn } from '@/utils';

const ChatLayout: React.FC<React.PropsWithChildren> = ({ children }) => {
  const { resetConversation } = useConversationStore();
  const {
    params: { deployment },
    setParams,
  } = useParamsStore();
  const { data: allDeployments } = useListAllDeployments();

  const { isRightPanelOpen } = useSettingsStore();
  const isDesktop = useIsDesktop();

  // Reset conversation when unmounting
  useEffect(() => {
    return () => {
      resetConversation();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!deployment && allDeployments) {
      const firstAvailableDeployment = allDeployments.find((d) => d.is_available);
      if (firstAvailableDeployment) {
        setParams({ deployment: firstAvailableDeployment.name });
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [deployment, allDeployments]);

  return (
    <div className="relative flex h-full">
      {children}
      <Transition
        show={isRightPanelOpen || isDesktop}
        as="div"
        className={cn(
          'border-marble-950 bg-marble-980 px-6 dark:border-volcanic-200 dark:bg-volcanic-100',
          'absolute inset-0 rounded-lg border lg:static lg:w-[360px] lg:rounded-none lg:rounded-r-lg lg:border-y lg:border-l-0 lg:border-r'
        )}
        enter="transition-all transform ease-in-out duration-300"
        enterFrom="translate-x-full"
        enterTo="translate-x-0"
        leave="transition-all transform ease-in-out duration-300"
        leaveFrom="translate-x-0 opacity-100"
        leaveTo="translate-x-full opacity-0"
      >
        <RightPanel />
      </Transition>
    </div>
  );
};

export default ChatLayout;
