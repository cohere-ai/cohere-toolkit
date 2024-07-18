'use client';
'use client';

import { Transition } from '@headlessui/react';
import React, { Children, PropsWithChildren, useContext, useEffect, useState } from 'react';

import { AgentsSidePanel } from '@/components/Agents/AgentsSidePanel';
import { DeploymentsDropdown } from '@/components/DeploymentsDropdown';
import { EditEnvVariablesButton } from '@/components/EditEnvVariablesButton';
import { MobileHeader } from '@/components/MobileHeader';
import { NavigationUserMenu } from '@/components/NavigationUserMenu';
import { SettingsDrawer } from '@/components/Settings/SettingsDrawer';
import { Banner } from '@/components/Shared';
import { NavigationBar } from '@/components/Shared/NavigationBar/NavigationBar';
import { BannerContext } from '@/context/BannerContext';
import { useIsDesktop } from '@/hooks/breakpoint';
import { useSession } from '@/hooks/session';
import { useSettingsStore } from '@/stores';
import { cn } from '@/utils/cn';

export const LeftSection: React.FC<React.PropsWithChildren> = ({ children }) => <>{children}</>;
export const MainSection: React.FC<React.PropsWithChildren> = ({ children }) => <>{children}</>;

type LayoutProps = {} & PropsWithChildren;

/**
 * This component is in charge of layout out the entire page.
 * It shows the navigation bar, the left drawer and main content.
 * On small devices (e.g. mobile), the left drawer and main section are stacked vertically.
 */
export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { message: bannerMessage } = useContext(BannerContext);
  const {
    settings: { isConvListPanelOpen, isMobileConvListPanelOpen },
  } = useSettingsStore();
  const isDesktop = useIsDesktop();
  const { session } = useSession();

  let leftDrawerElement: React.ReactNode = null;
  let mainElement: React.ReactNode = null;

  Children.toArray(children).forEach((child: React.ReactNode) => {
    const element = child as React.ReactElement;
    const { type } = element;

    switch (type) {
      case LeftSection:
        leftDrawerElement = child;
        break;
      case MainSection:
        mainElement = child;
        break;
      default:
        break;
    }
  });

  const [userMenu, setUserMenu] = useState<React.ReactNode>(null);

  useEffect(() => {
    if (session && session.email) {
      setUserMenu(<NavigationUserMenu userEmail={session.email} />);
    }
  }, [session]);

  return (
    <>
      <div className="flex h-screen w-full flex-1 flex-col gap-3 bg-mushroom-900 p-3">
        <NavigationBar>
          <span className="flex items-center gap-x-2">
            <DeploymentsDropdown />
            <EditEnvVariablesButton className="py-0" />
            {userMenu}
          </span>
        </NavigationBar>
        {bannerMessage && <Banner size="sm">{bannerMessage}</Banner>}

        <div className={cn('relative flex h-full flex-grow flex-nowrap overflow-hidden')}>
          <Transition
            as="div"
            show={isMobileConvListPanelOpen || (isConvListPanelOpen && isDesktop)}
            enterFrom={cn(
              '-translate-x-full lg:translate-x-0',
              'lg:mr-0 lg:opacity-0 lg:min-w-0 lg:max-w-0'
            )}
            enterTo={cn(
              'translate-x-0',
              'lg:mr-3 lg:opacity-100',
              'lg:min-w-left-panel-lg 2xl:min-w-left-panel-2xl 3xl:min-w-left-panel-3xl',
              'lg:max-w-left-panel-lg 2xl:max-w-left-panel-2xl 3xl:max-w-left-panel-3xl'
            )}
            leaveFrom={cn(
              'translate-x-0',
              'lg:mr-3 lg:opacity-100',
              'lg:min-w-left-panel-lg 2xl:min-w-left-panel-2xl 3xl:min-w-left-panel-3xl',
              'lg:max-w-left-panel-lg 2xl:max-w-left-panel-2xl 3xl:max-w-left-panel-3xl'
            )}
            leaveTo={cn(
              '-translate-x-full lg:translate-x-0',
              'lg:mr-0 lg:opacity-0 lg:border-0 lg:min-w-0 lg:max-w-0'
            )}
            className={cn(
              'lg:flex-grow-0',
              'transition-transform duration-500 ease-in-out',
              'lg:transition-[min-width,max-width,margin,opacity,border-width] lg:duration-300',
              'w-full',
              'flex flex-grow flex-col rounded-lg border',
              'border-marble-950 bg-marble-1000'
            )}
          >
            {leftDrawerElement}
          </Transition>
          <Transition
            as="main"
            show={!isMobileConvListPanelOpen || isDesktop}
            enterFrom="translate-x-full lg:translate-x-0"
            enterTo="translate-x-0"
            leaveFrom="translate-x-0"
            leaveTo="translate-x-full lg:translate-x-0"
            className={cn(
              'z-main-section flex flex-grow lg:min-w-0',
              'absolute h-full w-full lg:static lg:h-auto',
              'transition-transform duration-500 ease-in-out lg:transition-none'
            )}
          >
            <section
              className={cn(
                'relative flex h-full min-w-0 flex-grow flex-col',
                'rounded-lg border',
                'border-marble-950 bg-marble-1000',
                'overflow-hidden'
              )}
            >
              {mainElement}
            </section>
          </Transition>
          <SettingsDrawer />
        </div>
      </div>
    </>
  );
};

type AgentsLayoutProps = {
  title?: string;
  showSettingsDrawer?: boolean;
} & PropsWithChildren;

/**
 * @description This component is in charge of layout out the entire page when agents are available.
  It shows the navigation bar, the left drawer and main content.
  On small devices (e.g. mobile), the left drawer and main section are stacked vertically.
 */
export const AgentsLayout: React.FC<AgentsLayoutProps> = ({
  title = 'Chat',
  showSettingsDrawer = false,
  children,
}) => {
  let leftElement: React.ReactNode = null;
  let mainElement: React.ReactNode = null;

  Children.toArray(children).forEach((child: React.ReactNode) => {
    const element = child as React.ReactElement;

    if (element.type === LeftSection) {
      leftElement = child;
      return;
    }
    if (element.type === MainSection) {
      mainElement = child;
      return;
    }
  });

  return (
    <>
      <div className="dark:bg-vb-60 flex h-screen w-full flex-1 flex-col gap-3 bg-mushroom-900 p-3">
        <div
          className={cn(
            'relative flex h-full flex-grow flex-col flex-nowrap gap-3 overflow-hidden lg:flex-row'
          )}
        >
          <MobileHeader />
          <AgentsSidePanel className="hidden md:flex">{leftElement}</AgentsSidePanel>
          <section
            className={cn(
              'relative flex h-full min-w-0 flex-grow flex-col',
              'rounded-lg border',
              'border-marble-950 bg-marble-1000',
              'overflow-hidden'
            )}
          >
            {mainElement}
          </section>
          {showSettingsDrawer && <SettingsDrawer />}
        </div>
      </div>
      <AgentsSidePanel className="rounded-bl-none rounded-tl-none md:hidden">
        {leftElement}
      </AgentsSidePanel>
    </>
  );
};
