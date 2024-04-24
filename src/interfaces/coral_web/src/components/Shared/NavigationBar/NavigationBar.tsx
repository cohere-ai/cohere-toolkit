import cx from 'classnames';
import Link from 'next/link';
import React from 'react';

import { Logo } from '@/components/Shared';
import { DeploymentsDropdown } from '@/components/Shared/NavigationBar/DeploymentsDropdown';

/**
 * @description Displays the navigation bar where clicking the logo will return the user to the home page.
 */
export const NavigationBar: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <nav
      className={cx(
        'z-navigation flex w-full items-center justify-between rounded-lg border px-4 py-3',
        'border-marble-400 bg-marble-100',
        className
      )}
    >
      <Link href="/">
        <div className="mr-3 flex items-baseline">
          <Logo />
        </div>
      </Link>
      <DeploymentsDropdown />
    </nav>
  );
};
