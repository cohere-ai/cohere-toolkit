'use client';

import React, { Children, PropsWithChildren } from 'react';

import { AgentsSidePanel } from '@/components/Agents/AgentsSidePanel';
import { MobileHeader } from '@/components/MobileHeader';
import { cn } from '@/utils/cn';

export const LeftSection: React.FC<React.PropsWithChildren> = ({ children }) => <>{children}</>;
export const MainSection: React.FC<React.PropsWithChildren> = ({ children }) => <>{children}</>;

type Props = {} & PropsWithChildren;

/**
 * @description This component is in charge of layout out the entire page when agents are available.
  It shows the navigation bar, the left drawer and main content.
  On small devices (e.g. mobile), the left drawer and main section are stacked vertically.
 */
export const Layout: React.FC<Props> = ({ children }) => {
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
      <div className="flex h-screen w-full flex-1 flex-col gap-3 bg-mushroom-900 p-3 dark:bg-volcanic-60">
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
              'border-marble-950 bg-marble-1000 dark:border-volcanic-100 dark:bg-volcanic-100',
              'overflow-hidden'
            )}
          >
            {mainElement}
          </section>
        </div>
      </div>
      <AgentsSidePanel className="rounded-bl-none rounded-tl-none md:hidden">
        {leftElement}
      </AgentsSidePanel>
    </>
  );
};
