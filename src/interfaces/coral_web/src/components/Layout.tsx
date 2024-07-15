import { capitalize } from 'lodash';
import React, { Children, PropsWithChildren } from 'react';

import { AgentsSidePanel } from '@/components/Agents/AgentsSidePanel';
import { DeploymentsDropdown } from '@/components/DeploymentsDropdown';
import { EditEnvVariablesButton } from '@/components/EditEnvVariablesButton';
import { MobileHeader } from '@/components/MobileHeader';
import { NavigationUserMenu } from '@/components/NavigationUserMenu';
import { SettingsDrawer } from '@/components/Settings/SettingsDrawer';
import { PageHead } from '@/components/Shared/PageHead';
import { cn } from '@/utils/cn';

export const LeftSection: React.FC<React.PropsWithChildren> = ({ children }) => <>{children}</>;
export const MainSection: React.FC<React.PropsWithChildren> = ({ children }) => <>{children}</>;

type LayoutProps = {
  title?: string;
  showSettingsDrawer?: boolean;
} & PropsWithChildren;

/**
 * @description This component is in charge of layout out the entire page.
  It shows the navigation bar, the left drawer and main content.
  On small devices (e.g. mobile), the left drawer and main section are stacked vertically.
 */
export const Layout: React.FC<LayoutProps> = ({ title = 'Chat', children }) => {
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

  return (
    <>
      <PageHead title={capitalize(title)} />
      <div className="flex h-screen w-full flex-1 flex-col gap-3 bg-secondary-100 p-3">
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
              'border-marble-400 bg-marble-100',
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
      <PageHead title={capitalize(title)} />
      <div className="flex h-screen w-full flex-1 flex-col gap-3 bg-secondary-100 p-3">
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
              'border-marble-400 bg-marble-100',
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
