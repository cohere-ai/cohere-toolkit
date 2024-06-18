import { Transition } from '@headlessui/react';
import Link from 'next/link';

import IconButton from '@/components/IconButton';
import { Button, Icon, IconProps, Logo, Tooltip } from '@/components/Shared';
import { env } from '@/env.mjs';
import { useIsDesktop } from '@/hooks/breakpoint';
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

  const isDesktop = useIsDesktop();
  const isMobile = !isDesktop;

  const navigationItems: {
    label: string;
    icon: IconProps['name'];
    href?: string;
    onClick?: () => void;
  }[] = [
    { label: 'Create Assistant ', icon: 'add', href: '/agents/new' },
    { label: 'Discover', icon: 'compass', href: '/agents/discover' },
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
          'h-12 max-w-none flex-row px-2 py-2': isMobile,
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
          show={isAgentsSidePanelOpen}
          as="div"
          enter="transition-all transform ease-in-out duration-200"
          enterFrom="-translate-x-full"
          enterTo="translate-x-0"
        >
          <Link href="/" shallow>
            <div className="mr-3 flex items-baseline">
              <Logo hasCustomLogo={env.NEXT_PUBLIC_HAS_CUSTOM_LOGO === 'true'} />
            </div>
          </Link>
        </Transition>

        <IconButton
          iconName="close-drawer"
          onClick={() => setIsAgentsSidePanelOpen(!isAgentsSidePanelOpen)}
          className={cn('transition delay-100 duration-200 ease-in-out', {
            'rotate-180 transform text-secondary-700': isAgentsSidePanelOpen,
            hidden: isMobile,
          })}
        />
      </div>
      <div className="flex-grow overflow-y-auto">{children}</div>
      {isAgentsSidePanelOpen ? (
        <div className={cn('flex flex-shrink-0 flex-col gap-y-4')}>
          {navigationItems.map(({ label, icon, href, onClick }) => (
            <Button
              key={label}
              kind="secondary"
              className="truncate text-secondary-900"
              startIcon={<Icon name={icon} kind="outline" className="text-secondary-900" />}
              label={label}
              href={href}
              shallow
              onClick={onClick}
            />
          ))}
        </div>
      ) : (
        <div
          className={cn('flex flex-shrink-0 flex-col items-center gap-y-4', {
            'mr-2 flex-row gap-x-1': isMobile,
          })}
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
        </div>
      )}
    </div>
  );
};
