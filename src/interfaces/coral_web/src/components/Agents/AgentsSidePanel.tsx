import { Transition } from '@headlessui/react';
import Link from 'next/link';

import IconButton from '@/components/IconButton';
import { Button, Icon, IconProps, Logo, Tooltip } from '@/components/Shared';
import { env } from '@/env.mjs';
import { useSettingsStore } from '@/stores';
import { cn } from '@/utils';

/**
 * @description This component renders the agents side panel.
 * It contains the logo and a button to expand or collapse the panel.
 * It also renders the children components that are passed to it.
 */
export const AgentsSidePanel: React.FC<React.PropsWithChildren> = ({ children }) => {
  const {
    settings: { isAgentsSidePanelOpen },
    setIsAgentsSidePanelOpen,
  } = useSettingsStore();

  const navigationItems: {
    label: string;
    icon: IconProps['name'];
    href?: string;
    onClick?: () => void;
  }[] = [
    { label: 'Create Assistant ', icon: 'add', href: '/agents/new' },
    { label: 'Sign Out', icon: 'profile', onClick: () => void 0 },
  ];

  return (
    <div
      className={cn(
        'box-content px-4 py-6',
        'flex flex-grow flex-col gap-y-8 rounded-lg border',
        'border-marble-400 bg-marble-100',
        'transition-[min-width,max-width]',
        {
          'min-w-12 max-w-12': !isAgentsSidePanelOpen,
          'min-w-64 max-w-64': isAgentsSidePanelOpen,
        }
      )}
    >
      <div
        className={cn('flex flex-shrink-0 items-center', {
          'justify-between gap-x-3': isAgentsSidePanelOpen,
          'justify-center': !isAgentsSidePanelOpen,
        })}
      >
        {isAgentsSidePanelOpen && (
          <Link href="/" shallow>
            <div className="mr-3 flex items-baseline">
              <Logo hasCustomLogo={env.NEXT_PUBLIC_HAS_CUSTOM_LOGO === 'true'} />
            </div>
          </Link>
        )}
        <IconButton
          iconName="close-drawer"
          onClick={() => setIsAgentsSidePanelOpen(!isAgentsSidePanelOpen)}
          className={cn('transition delay-100 duration-200 ease-in-out', {
            'rotate-180 transform text-secondary-700': isAgentsSidePanelOpen,
          })}
        />
      </div>
      <div className="flex-grow overflow-y-auto">{children}</div>
      <Transition
        show={!isAgentsSidePanelOpen}
        as="div"
        className="flex flex-shrink-0 flex-col gap-y-4"
        enter="transition-opacity duration-100 ease-in-out delay-300"
        enterFrom="opacity-0"
        enterTo="opacity-100"
      >
        {navigationItems.map(({ label, icon, href, onClick }) => (
          <Tooltip key={label} label={label} hover placement="right">
            <IconButton
              iconName={icon}
              iconClassName="text-secondary-900"
              shallow
              onClick={onClick}
              href={href}
              className="w-full text-secondary-900"
            />
          </Tooltip>
        ))}
      </Transition>
      <Transition
        show={isAgentsSidePanelOpen}
        as="div"
        className="flex flex-shrink-0 flex-col gap-y-4"
        enter="transition-opacity duration-100 ease-in-out delay-300"
        enterFrom="opacity-0"
        enterTo="opacity-100"
      >
        {navigationItems.map(({ label, icon, href, onClick }) => (
          <Button
            key={label}
            kind="secondary"
            className="text-secondary-900"
            startIcon={<Icon name={icon} className="text-secondary-900" />}
            label={label}
            href={href}
            onClick={onClick}
          />
        ))}
      </Transition>
    </div>
  );
};
