'use client';

import { Transition } from '@headlessui/react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import React from 'react';

import { Button, Logo, Text, Tooltip } from '@/components/Shared';
import { Shortcut } from '@/components/Shortcut';
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
  const router = useRouter();
  const {
    agents: { isAgentsSidePanelOpen },
  } = useAgentsStore();
  const isDesktop = useIsDesktop();
  const isMobile = !isDesktop;

  const { setEditAgentPanelOpen } = useAgentsStore();
  const { resetConversation } = useConversationStore();
  const { resetCitations } = useCitationsStore();
  const { resetFileParams } = useParamsStore();

  const handleNewChat = () => {
    const url = '/';
    setEditAgentPanelOpen(false);
    resetConversation();
    resetCitations();
    resetFileParams();
    router.push(url);
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
          'md:transition-[min-width,max-width]',
          {
            'gap-y-4 md:min-w-agents-panel-collapsed md:max-w-agents-panel-collapsed':
              !isAgentsSidePanelOpen,
            'md:min-w-agents-panel-expanded md:max-w-agents-panel-expanded lg:min-w-agents-panel-expanded-lg lg:max-w-agents-panel-expanded-lg':
              isAgentsSidePanelOpen,
          }
        )}
      >
        <div
          className={cn('flex flex-shrink-0 items-center', {
            'justify-center': !isAgentsSidePanelOpen,
            'justify-between gap-x-3': isMobile && isAgentsSidePanelOpen,
          })}
        >
          <Link href="/">
            <Logo
              hasCustomLogo={env.NEXT_PUBLIC_HAS_CUSTOM_LOGO}
              includeBrandName={isAgentsSidePanelOpen}
            />
          </Link>

          <ToggleAgentsSidePanelButton className="flex md:hidden" />
        </div>

        <div
          className={cn('flex flex-shrink-0 flex-col gap-y-4', {
            'items-center': !isAgentsSidePanelOpen,
          })}
        >
          <Button
            kind="secondary"
            label={
              <div className="group flex items-center justify-between">
                <Text className="dark:text-evolved-green-700">New chat</Text>
                <Shortcut sequence={['⌘', '↑', 'N']} className="hidden group-hover:flex" />
              </div>
            }
            icon="add"
            theme="evolved-green"
            onClick={handleNewChat}
          />

          <Button kind="secondary" label="See all assistants" href="/discover" icon="compass" />
        </div>

        <div className={cn('flex-grow overflow-y-auto')}>{children}</div>

        <footer className={cn('flex flex-col gap-4', { 'items-center': !isAgentsSidePanelOpen })}>
          <Button label="Settings" href="/settings" icon="settings" kind="secondary" />
          <section className="flex items-center justify-between">
            <div
              className={cn('flex items-center gap-2', {
                hidden: !isAgentsSidePanelOpen,
              })}
            >
              <Text styleAs="label" className="dark:text-mushroom-800">
                POWERED BY
              </Text>
              <Logo hasCustomLogo={env.NEXT_PUBLIC_HAS_CUSTOM_LOGO} includeBrandName={false} />
            </div>
            <ToggleAgentsSidePanelButton className="hidden md:flex" />
          </section>
        </footer>
      </div>
    </Transition>
  );
};

const ToggleAgentsSidePanelButton: React.FC<{ className?: string }> = ({ className }) => {
  const {
    agents: { isAgentsSidePanelOpen },
    setAgentsSidePanelOpen,
  } = useAgentsStore();
  const { setSettings, setIsConvListPanelOpen } = useSettingsStore();

  const handleToggleAgentsSidePanel = () => {
    setIsConvListPanelOpen(false);
    setSettings({ isConfigDrawerOpen: false });
    setAgentsSidePanelOpen(!isAgentsSidePanelOpen);
  };

  return (
    <Tooltip hover label="Toggle agents side panel">
      <Button
        kind="secondary"
        className="px-2"
        icon="close-drawer"
        iconOptions={{
          className: cn('transform transition delay-100 duration-200 ease-in-out', className, {
            'rotate-180 ': isAgentsSidePanelOpen,
          }),
        }}
        animate={false}
        onClick={handleToggleAgentsSidePanel}
      />
    </Tooltip>
  );
};
