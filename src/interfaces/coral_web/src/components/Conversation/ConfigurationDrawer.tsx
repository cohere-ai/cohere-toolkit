import { Transition } from '@headlessui/react';
import React from 'react';

import { Configuration } from '@/components/Configuration';
import { IconButton } from '@/components/IconButton';
import { Icon, Text } from '@/components/Shared';
import { useCitationsStore, useSettingsStore } from '@/stores';
import { cn } from '@/utils';

/**
 * @description Renders the configuration drawer of the main content.
 * It opens up on top of the citation panel/the main content.
 */
export const ConfigurationDrawer: React.FC = () => {
  const {
    settings: { isConfigDrawerOpen },
    setSettings,
  } = useSettingsStore();
  const {
    citations: { hasCitations },
  } = useCitationsStore();

  return (
    <Transition
      as="section"
      show={isConfigDrawerOpen}
      className={cn(
        'absolute right-0 z-configuration-drawer',
        'flex h-full flex-col',
        'w-full md:max-w-drawer lg:max-w-drawer-lg',
        'rounded-lg md:rounded-l-none',
        'bg-marble-100 md:shadow-drawer',
        'border border-marble-400',
        { 'xl:border-l-0': hasCitations }
      )}
      enter="transition-transform ease-in-out duration-200"
      enterFrom="translate-x-full"
      enterTo="translate-x-0"
      leave="transition-transform ease-in-out duration-200"
      leaveFrom="translate-x-0"
      leaveTo="translate-x-full"
    >
      <header className="flex h-header items-center gap-2 border-b border-marble-400 p-5">
        <IconButton
          iconName="close-drawer"
          tooltip={{ label: 'Close drawer', size: 'md' }}
          isDefaultOnHover={false}
          onClick={() => setSettings({ isConfigDrawerOpen: false })}
        />
        <span className="flex items-center gap-2">
          <Icon name="settings" className="text-volcanic-700" kind="outline" />
          <Text styleAs="p-lg">Settings</Text>
        </span>
      </header>
      <Configuration />
    </Transition>
  );
};
