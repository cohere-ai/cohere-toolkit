'use client';

import { Popover, Transition } from '@headlessui/react';
import { Fragment } from 'react';

import { AuthLink } from '@/components/AuthLink';
import { Icon, Text } from '@/components/Shared';
import { cn } from '@/utils';

/**
 * Popover menu that shows a user's email and a button to logout when logged in.
 * When a user is logged out it shows a button to "Sign in" which redirects
 * back to the current route after successfully signing in.
 */
export const NavigationUserMenu: React.FC<{
  userEmail?: string;
  showEmail?: boolean;
}> = ({ userEmail, showEmail = false }) => {
  return (
    <PopoverMenu email={showEmail && userEmail ? userEmail : undefined}>
      <div className="py-3">
        <Icon name="profile" className="mb-3 px-4 text-volcanic-400" />
        {userEmail ? (
          <>
            <Text className="truncate px-4 pb-3 text-left text-volcanic-400">{userEmail}</Text>
            <div className="flex justify-end border-t border-marble-950 px-4 pt-3">
              <AuthLink action="logout" styleAs="button" kind="secondary" />
            </div>
          </>
        ) : (
          <div className="mt-3 flex justify-end border-t border-marble-950 px-4 pt-3">
            <AuthLink action="login" styleAs="button" kind="secondary" />
          </div>
        )}
      </div>
    </PopoverMenu>
  );
};

/**
 * Popover menu that opens when the menu icon is clicked.
 * Only used on > md.
 */
const PopoverMenu: React.FC<{
  className?: string;
  children?: React.ReactNode;
  email?: string;
  darkModeEnabled?: boolean;
}> = ({ className = '', email, darkModeEnabled, children }) => {
  return (
    <Popover className={cn('relative', className)}>
      <Popover.Button
        className={cn(
          'flex items-center gap-x-2 px-1 focus:rounded focus:outline focus:outline-1 focus:outline-offset-4',
          'focus:outline-volcanic-400',
          { 'dark:focus:outline-marble-800': darkModeEnabled }
        )}
      >
        <Icon name="profile" size="md" />
        {email && <Text className="hidden md:block">{email}</Text>}
      </Popover.Button>
      <Transition
        as={Fragment}
        enter="transition ease-out duration-200"
        enterFrom="opacity-0 translate-y-1"
        enterTo="opacity-100 translate-y-0"
        leave="transition ease-in duration-150"
        leaveFrom="opacity-100 translate-y-0"
        leaveTo="opacity-0 translate-y-1"
      >
        <Popover.Panel
          className={cn(
            'absolute right-0 top-11 z-navigation w-60 rounded-lg border',
            'border-marble-950 bg-marble-1000',
            { 'dark:border-dark-border dark:bg-dark-white-2-solid': darkModeEnabled }
          )}
        >
          {children}
        </Popover.Panel>
      </Transition>
    </Popover>
  );
};
