'use client';

import { Transition } from '@headlessui/react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

import { IconButton } from '@/components/IconButton';
import { Button, Icon, Logo, Text } from '@/components/Shared';
import { env } from '@/env.mjs';
import { useIsDesktop } from '@/hooks/breakpoint';
import {
  useAgentsStore,
  useCitationsStore,
  useConversationStore,
  useParamsStore,
  useSettingsStore,
} from '@/stores';
import { cn } from '@/utils';

/**
 * @description This component renders the agents side panel.
 * It contains the logo and a button to expand or collapse the panel.
 * It also renders the children components that are passed to it.
 */
export const AgentsSidePanel: React.FC<React.PropsWithChildren<{ className?: string }>> = ({
  className = '',
  children,
}) => {
  const { setSettings, setIsConvListPanelOpen } = useSettingsStore();
  const router = useRouter();
  const {
    agents: { isAgentsSidePanelOpen },
    setAgentsSidePanelOpen,
  } = useAgentsStore();
  const isDesktop = useIsDesktop();
  const isMobile = !isDesktop;

  const handleToggleAgentsSidePanel = () => {
    setIsConvListPanelOpen(false);
    setSettings({ isConfigDrawerOpen: false });
    setAgentsSidePanelOpen(!isAgentsSidePanelOpen);
  };

  const { setEditAgentPanelOpen } = useAgentsStore();
  const { resetConversation } = useConversationStore();
  const { resetCitations } = useCitationsStore();
  const { resetFileParams } = useParamsStore();

  const handleNewChat = () => {
    const url = '/';
    router.push(url, undefined);
    setEditAgentPanelOpen(false);
    resetConversation();
    resetCitations();
    resetFileParams();
  };

  return (
    <Transition
      show={isAgentsSidePanelOpen || isDesktop}
      as="div"
      className={cn(
        'absolute bottom-0 left-0 top-0 z-30 lg:static',
        'h-full bg-marble-1000 dark:bg-volcanic-60',
        'rounded-lg border border-marble-950 dark:border-volcanic-60',
        'dark:text-mushroom-950',
        {
          'right-1/4 md:right-auto': isAgentsSidePanelOpen,
        },
        className
      )}
      enter="transition-all transform ease-in-out duration-500"
      enterFrom="-translate-x-full"
      enterTo="translate-x-0"
      leave="transition-all transform ease-in-out duration-500"
      leaveFrom="translate-x-0 opacity-100"
      leaveTo="-translate-x-full opacity-0"
    >
      <div
        className={cn(
          'flex h-full flex-grow flex-col gap-y-8 px-4 py-6',
          'md:min-w-agents-panel-expanded md:max-w-agents-panel-expanded lg:min-w-agents-panel-expanded-lg lg:max-w-agents-panel-expanded-lg'
        )}
      >
        <div
          className={cn('flex flex-shrink-0 items-center', {
            'justify-between gap-x-3': isAgentsSidePanelOpen || isMobile,
          })}
        >
          <Link href="/" shallow>
            <div className="mr-3 flex items-baseline">
              <Logo hasCustomLogo={env.NEXT_PUBLIC_HAS_CUSTOM_LOGO === 'true'} />
            </div>
          </Link>

          <IconButton
            iconName="close-drawer"
            onClick={handleToggleAgentsSidePanel}
            className={cn(
              'flex text-mushroom-950 transition delay-100 duration-200 ease-in-out md:hidden',
              {
                'rotate-180 transform': isAgentsSidePanelOpen,
              }
            )}
          />
        </div>

        <div className="flex flex-shrink-0 flex-col gap-y-4">
          <Button
            kind="secondary"
            className="truncate [&_span]:text-evolved-green-700"
            startIcon={<Icon name="add" kind="outline" className="text-evolved-green-700" />}
            label="New chat"
            onClick={handleNewChat}
            shallow
          />
          <Button
            kind="secondary"
            className="truncate [&_span]:text-mushroom-950"
            startIcon={<Icon name="compass" kind="outline" className="text-mushroom-950" />}
            label="See all assistants"
            href="/discover"
            shallow
          />
        </div>

        <div className="flex-grow overflow-y-auto">{children}</div>

        <footer className="flex flex-col gap-4">
          <Button
            kind="secondary"
            className="truncate [&_span]:text-mushroom-950"
            startIcon={<Icon name="settings" kind="outline" className="text-mushroom-950" />}
            label="Settings"
            href="/settings"
            shallow
          />
          <section className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Text styleAs="label" className="text-mushroom-800">
                POWERED BY
              </Text>
              <Logo
                hasCustomLogo={env.NEXT_PUBLIC_HAS_CUSTOM_LOGO === 'true'}
                includeBrandName={false}
              />
            </div>
          </section>
        </footer>
      </div>
    </Transition>
  );
};
