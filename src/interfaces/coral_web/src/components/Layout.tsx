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

const LeftDrawer: React.FC<PropsWithChildren> = ({ children }) => <>{children}</>;
const Main: React.FC<PropsWithChildren> = ({ children }) => <>{children}</>;

export const LayoutSection = {
  LeftDrawer,
  Main,
};

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

  let leftDrawerElement: React.ReactNode = null;
  let mainElement: React.ReactNode = null;

  Children.toArray(children).forEach((child: React.ReactNode) => {
    const element = child as React.ReactElement;
    const { type } = element;

    switch (type) {
      case LeftDrawer:
        leftDrawerElement = child;
        break;
      case Main:
        mainElement = child;
        break;
      default:
        break;
    }
  });

  return (
    <>
      <PageHead title={capitalize(title)} />
      <div className="flex h-screen w-full flex-1 flex-col gap-3 bg-secondary-100 p-3">
        {/* <NavigationBar>
          <span className="flex items-center gap-x-2">
            <DeploymentsDropdown />
            <EditEnvVariablesButton className="py-0" />
          </span>
        </NavigationBar> */}
        {bannerMessage && <Banner size="sm">{bannerMessage}</Banner>}

        <div className={cn('relative flex h-full flex-grow flex-nowrap overflow-hidden')}>
          <Transition
            as="div"
            show={false}
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
              'border-marble-400 bg-marble-100'
            )}
          >
            {leftDrawerElement}
          </Transition>
          <Transition
            as="main"
            show={true}
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
