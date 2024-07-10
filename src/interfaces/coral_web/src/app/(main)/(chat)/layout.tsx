'use client';

import { Transition } from '@headlessui/react';

import ConversationListPanel from '@/components/ConversationList/ConversationListPanel';
import { useIsDesktop } from '@/hooks/breakpoint';
import { useSettingsStore } from '@/stores';
import { cn } from '@/utils';

const ChatLayout: React.FC<React.PropsWithChildren> = ({ children }) => {
  const {
    settings: { isConvListPanelOpen, isMobileConvListPanelOpen },
  } = useSettingsStore();

  const isDesktop = useIsDesktop();
  const isMobile = !isDesktop;

  return (
    <div className="flex h-full">
      <Transition
        as="section"
        show={(isMobileConvListPanelOpen && isMobile) || (isConvListPanelOpen && isDesktop)}
        enterFrom="translate-x-full lg:translate-x-0 lg:min-w-0 lg:max-w-0"
        enterTo="translate-x-0 lg:min-w-[300px] lg:max-w-[300px]"
        leaveFrom="translate-x-0 lg:min-w-[300px] lg:max-w-[300px]"
        leaveTo="translate-x-full lg:translate-x-0 lg:min-w-0 lg:max-w-0"
        className={cn(
          'z-main-section flex lg:min-w-0',
          'absolute h-full w-full lg:static lg:h-auto',
          'border-0 border-marble-400 md:border-r',
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
};

export default ChatLayout;
