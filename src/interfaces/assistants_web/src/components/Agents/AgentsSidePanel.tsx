'use client';

import { Transition } from '@headlessui/react';
import React, { ReactElement } from 'react';

import { IconButton } from '@/components/IconButton';
import { Button, Icon, Logo, Text } from '@/components/Shared';
import { Shortcut } from '@/components/Shortcut';
import { env } from '@/env.mjs';
import { useIsDesktop } from '@/hooks/breakpoint';
import { useNavigateToNewChat } from '@/hooks/chatRoutes';
import { useAgentsStore, useSettingsStore } from '@/stores';
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
  const {
    agents: { isAgentsSidePanelOpen },
  } = useAgentsStore();
  const isDesktop = useIsDesktop();
  const isMobile = !isDesktop;

  const navigateToNewChat = useNavigateToNewChat();

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
          <button onClick={() => navigateToNewChat()}>
            <Logo
              hasCustomLogo={env.NEXT_PUBLIC_HAS_CUSTOM_LOGO}
              includeBrandName={isAgentsSidePanelOpen}
            />
          </button>

          <ToggleAgentsSidePanelButton className="flex md:hidden" />
        </div>

        <div
          className={cn('flex flex-shrink-0 flex-col gap-y-4', {
            'items-center': !isAgentsSidePanelOpen,
          })}
        >
          <SidePanelButton
            label={
              <div className="group flex items-center justify-between">
                <Text className="dark:text-evolved-green-700">New chat</Text>
                <Shortcut sequence={['⌘', '↑', 'N']} className="hidden group-hover:flex" />
              </div>
            }
            onClick={() => navigateToNewChat()}
            tooltip="New chat"
            icon={<Icon name="add" kind="outline" className="dark:text-evolved-green-700" />}
          />
          <SidePanelButton
            label="See all assistants"
            tooltip="See all assistants"
            href="/discover"
            icon={<Icon name="compass" kind="outline" className="dark:text-mushroom-950" />}
          />
        </div>

        <div className={cn('flex-grow overflow-y-auto')}>{children}</div>

        <footer className={cn('flex flex-col gap-4', { 'items-center': !isAgentsSidePanelOpen })}>
          <SidePanelButton
            label="Settings"
            tooltip="Settings"
            href="/settings"
            icon={<Icon name="settings" kind="outline" className="dark:text-mushroom-950" />}
          />
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

const SidePanelButton: React.FC<{
  label?: ReactElement | string;
  tooltip?: string;
  href?: string;
  onClick?: VoidFunction;
  icon: ReactElement;
  className?: string;
}> = ({ label, tooltip, href, icon, className, onClick }) => {
  const {
    agents: { isAgentsSidePanelOpen },
  } = useAgentsStore();

  if (isAgentsSidePanelOpen) {
    return (
      <Button
        kind="secondary"
        className={cn('dark:[&_span]:text-mushroom-950', className)}
        startIcon={icon}
        label={label}
        href={href}
        onClick={onClick}
      />
    );
  }

  return (
    <IconButton
      icon={icon}
      href={href}
      onClick={onClick}
      className={className}
      tooltip={tooltip ? { label: tooltip } : undefined}
    />
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
    <IconButton
      iconName="close-drawer"
      onClick={handleToggleAgentsSidePanel}
      tooltip={{ label: 'Toggle agents side panel' }}
      className={cn(
        'transform transition delay-100 duration-200 ease-in-out dark:text-mushroom-950 dark:hover:text-mushroom-950',
        className,
        {
          'rotate-180 ': isAgentsSidePanelOpen,
        }
      )}
    />
  );
};
