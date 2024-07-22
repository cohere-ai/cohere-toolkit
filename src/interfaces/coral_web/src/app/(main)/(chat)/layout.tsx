'use client';

import { Transition } from '@headlessui/react';
import { useContext, useEffect } from 'react';

import ConversationListPanel from '@/components/ConversationList/ConversationListPanel';
import { BannerContext } from '@/context/BannerContext';
import { useIsDesktop } from '@/hooks/breakpoint';
import { useListAllDeployments } from '@/hooks/deployments';
import { useExperimentalFeatures } from '@/hooks/experimentalFeatures';
import { useConversationStore, useParamsStore, useSettingsStore } from '@/stores';
import { cn } from '@/utils';

const ChatLayout: React.FC<React.PropsWithChildren> = ({ children }) => {
  const { data: experimentalFeatures } = useExperimentalFeatures();
  const isAgentsModeOn = !!experimentalFeatures?.USE_AGENTS_VIEW;
  const {
    settings: { isConvListPanelOpen, isMobileConvListPanelOpen },
  } = useSettingsStore();
  const { resetConversation } = useConversationStore();
  const {
    params: { deployment },
    setParams,
  } = useParamsStore();
  const { data: allDeployments } = useListAllDeployments();

  const isLangchainModeOn = !!experimentalFeatures?.USE_EXPERIMENTAL_LANGCHAIN;
  const { setMessage } = useContext(BannerContext);

  const isDesktop = useIsDesktop();
  const isMobile = !isDesktop;

  // Reset conversation when unmounting
  useEffect(() => {
    return () => {
      resetConversation();
    };
  }, []);

  useEffect(() => {
    if (!deployment && allDeployments) {
      const firstAvailableDeployment = allDeployments.find((d) => d.is_available);
      if (firstAvailableDeployment) {
        setParams({ deployment: firstAvailableDeployment.name });
      }
    }
  }, [deployment, allDeployments]);

  useEffect(() => {
    if (!isLangchainModeOn) return;
    setMessage('You are using an experimental langchain multihop flow. There will be bugs.');
  }, [isLangchainModeOn]);

  if (isAgentsModeOn) {
    return (
      <div className="flex h-full">
        <Transition
          as="section"
          appear
          show={(isMobileConvListPanelOpen && isMobile) || (isConvListPanelOpen && isDesktop)}
          enterFrom="translate-x-full lg:translate-x-0 lg:min-w-0 lg:max-w-0"
          enterTo="translate-x-0 lg:min-w-[300px] lg:max-w-[300px]"
          leaveFrom="translate-x-0 lg:min-w-[300px] lg:max-w-[300px]"
          leaveTo="translate-x-full lg:translate-x-0 lg:min-w-0 lg:max-w-0"
          className={cn(
            'z-main-section flex lg:min-w-0',
            'absolute h-full w-full lg:static lg:h-auto',
            'border-0 border-marble-950 md:border-r',
            'transition-[transform,min-width,max-width] duration-300 ease-in-out'
          )}
        >
          <ConversationListPanel />
        </Transition>
        <Transition
          as="main"
          show={isDesktop || !isMobileConvListPanelOpen}
          enterFrom="-translate-x-full"
          enterTo="translate-x-0"
          leaveFrom="translate-x-0"
          leaveTo="-translate-x-full"
          className={cn(
            'flex min-w-0 flex-grow flex-col',
            'transition-transform duration-500 ease-in-out'
          )}
        >
          {children}
        </Transition>
      </div>
    );
  } else {
    return children;
  }
};

export default ChatLayout;
