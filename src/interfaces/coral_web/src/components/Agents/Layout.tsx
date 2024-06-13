import { Transition } from '@headlessui/react';
import { capitalize } from 'lodash';
import React, { Children, PropsWithChildren, useContext } from 'react';

import { ConfigurationDrawer } from '@/components/Conversation/ConfigurationDrawer';
import { DeploymentsDropdown } from '@/components/DeploymentsDropdown';
import { EditEnvVariablesButton } from '@/components/EditEnvVariablesButton';
import { Banner } from '@/components/Shared';
import { NavigationBar } from '@/components/Shared/NavigationBar/NavigationBar';
import { PageHead } from '@/components/Shared/PageHead';
import { BannerContext } from '@/context/BannerContext';
import { useIsDesktop } from '@/hooks/breakpoint';
import { useSettingsStore } from '@/stores';
import { cn } from '@/utils/cn';

export const LeftSection: React.FC<React.PropsWithChildren> = ({ children }) => <>{children}</>;
export const MainSection: React.FC<React.PropsWithChildren> = ({ children }) => <>{children}</>;

type Props = {
  title?: string;
} & PropsWithChildren;

/**
 * This component is in charge of layout out the entire page.
 * It shows the navigation bar, the left drawer and main content.
 * On small devices (e.g. mobile), the left drawer and main section are stacked vertically.
 */
export const Layout: React.FC<Props> = ({ title = 'Chat', children }) => {
  const { message: bannerMessage } = useContext(BannerContext);
  const {
    settings: { isConvListPanelOpen, isMobileConvListPanelOpen },
  } = useSettingsStore();
  const isDesktop = useIsDesktop();

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
      <PageHead title={capitalize(title)} />
      <div className="flex h-screen w-full flex-1 flex-col gap-3 bg-secondary-100 p-3">
        <NavigationBar>
          <span className="flex items-center gap-x-2">
            <DeploymentsDropdown />
            <EditEnvVariablesButton className="py-0" />
          </span>
        </NavigationBar>
        {bannerMessage && <Banner size="sm">{bannerMessage}</Banner>}

        <div className={cn('relative flex h-full flex-grow flex-nowrap gap-3 overflow-hidden')}>
          <div
            className={cn(
              'w-16 px-4 py-6 lg:flex-grow-0',
              'flex flex-grow flex-col rounded-lg border',
              'border-marble-400 bg-marble-100'
            )}
          >
            {leftElement}
          </div>
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
                'border-marble-400 bg-marble-100',
                'overflow-hidden'
              )}
            >
              {mainElement}
            </section>
          </Transition>
          <ConfigurationDrawer />
        </div>
      </div>
    </>
  );
};
