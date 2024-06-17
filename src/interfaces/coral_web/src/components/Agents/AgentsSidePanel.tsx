import { Transition } from '@headlessui/react';
import Link from 'next/link';

import { Button, Icon, Logo } from '@/components/Shared';
import { env } from '@/env.mjs';
import { useSettingsStore } from '@/stores';
import { cn } from '@/utils';

/**
 * This component renders the agents side panel.
 * It contains the logo and a button to expand or collapse the panel.
 * It also renders the children components that are passed to it.
 */
export const AgentsSidePanel: React.FC<React.PropsWithChildren> = ({ children }) => {
  const {
    settings: { isAgentsSidePanelOpen },
    setIsAgentsSidePanelOpen,
  } = useSettingsStore();

  return (
    <div
      className={cn(
        'box-content px-4 py-6',
        'flex flex-grow flex-col gap-y-8 rounded-lg border',
        'border-marble-400 bg-marble-100',
        'transition-[width]',
        {
          'w-12': !isAgentsSidePanelOpen,
          'w-64': isAgentsSidePanelOpen,
        }
      )}
    >
      <div
        className={cn('flex flex-shrink-0 items-center', {
          'justify-between gap-x-3': isAgentsSidePanelOpen,
          'justify-center': !isAgentsSidePanelOpen,
        })}
      >
        <Transition
          as="div"
          show={isAgentsSidePanelOpen}
          enter="transition-transform duration-100 ease-in-out"
          enterFrom="-translate-x-full"
          enterTo="translate-x-0"
          leave="transition-transform duration-100 ease-in-out"
          leaveFrom="translate-x-0"
          leaveTo="-translate-x-full"
        >
          <Link href="/">
            <div className="mr-3 flex items-baseline">
              <Logo hasCustomLogo={env.NEXT_PUBLIC_HAS_CUSTOM_LOGO === 'true'} />
            </div>
          </Link>
        </Transition>
        <button
          onClick={() => setIsAgentsSidePanelOpen(!isAgentsSidePanelOpen)}
          className={cn('transition delay-100 duration-200 ease-in-out', {
            'rotate-180 transform text-secondary-700': isAgentsSidePanelOpen,
          })}
        >
          <Icon name="close-drawer" />
        </button>
      </div>
      <div className="flex-grow overflow-y-auto">{children}</div>
      <div className="flex flex-shrink-0 flex-col gap-y-4">
        <Button
          kind="secondary"
          className="text-secondary-900"
          startIcon={<Icon name="add" className="text-secondary-900" />}
          label="Create Assistant"
          href="/agents/new"
        />
        <Button
          kind="secondary"
          className="text-secondary-900"
          startIcon={<Icon name="profile" className="text-secondary-900" />}
          label="Sign out"
        />
      </div>
    </div>
  );
};
