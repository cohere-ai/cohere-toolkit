'use client';

import { capitalize } from 'lodash';
import React from 'react';

import { AgentsSidePanel } from '@/components/Agents/AgentsSidePanel';
import { MobileHeader } from '@/components/MobileHeader';
import { SettingsDrawer } from '@/components/Settings/SettingsDrawer';
import { PageHead } from '@/components/Shared/PageHead';
import { cn } from '@/utils/cn';

type Props = {
  title?: string;
  showSettingsDrawer?: boolean;
  leftElement?: React.ReactNode;
  mainElement?: React.ReactNode;
};

/**
 * @description This component is in charge of layout out the entire page.
  It shows the navigation bar, the left drawer and main content.
  On small devices (e.g. mobile), the left drawer and main section are stacked vertically.
 */
export const Layout: React.FC<Props> = ({
  title = 'Chat',
  showSettingsDrawer = false,
  leftElement,
  mainElement,
}) => {
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
