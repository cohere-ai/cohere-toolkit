'use client';
'use client';

import React, { Children, PropsWithChildren } from 'react';

import { AgentsSidePanel } from '@/components/Agents/AgentsSidePanel';
import { MobileHeader } from '@/components/MobileHeader';
import { SettingsDrawer } from '@/components/Settings/SettingsDrawer';
import { cn } from '@/utils/cn';

export const LeftSection: React.FC<React.PropsWithChildren> = ({ children }) => <>{children}</>;
export const MainSection: React.FC<React.PropsWithChildren> = ({ children }) => <>{children}</>;

type Props = {
  title?: string;
  showSettingsDrawer?: boolean;
} & PropsWithChildren;

/**
 *
 */
export const Layout: React.FC<Props> = ({ showSettingsDrawer = false, children }) => {
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
