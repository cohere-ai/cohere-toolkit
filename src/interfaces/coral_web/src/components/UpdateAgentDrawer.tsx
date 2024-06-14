import { Transition } from '@headlessui/react';
import React from 'react';

import { Agent } from '@/cohere-client';
import IconButton from '@/components/IconButton';
import { Button, Text } from '@/components/Shared';
import { useSettingsStore } from '@/stores';
import { cn } from '@/utils';

type Props = {
  agent: Agent;
};

export const UpdateAgentDrawer: React.FC<Props> = ({ agent }) => {
  const {
    settings: { isEditAgentDrawerOpen },
    setSettings,
  } = useSettingsStore();
  const canSubmit = false;

  const handleClose = () => {
    setSettings({ isEditAgentDrawerOpen: false });
  };

  const handleUpdate = () => {
    if (!canSubmit) return;
  };

  return (
    <Transition
      as="section"
      show={isEditAgentDrawerOpen}
      className={cn(
        'absolute right-0 z-configuration-drawer',
        'flex h-full flex-col',
        'w-full md:max-w-agent-drawer lg:max-w-agent-drawer-lg',
        'rounded-lg md:rounded-l-none',
        'bg-marble-100 md:shadow-drawer',
        'border border-marble-400'
      )}
      enter="transition-transform ease-in-out duration-200"
      enterFrom="translate-x-full"
      enterTo="translate-x-0"
      leave="transition-transform ease-in-out duration-200"
      leaveFrom="translate-x-0"
      leaveTo="translate-x-full"
    >
      <header className="flex items-center justify-between border-b border-marble-400 py-5 pl-14 pr-6">
        <Text>Update {agent.name}</Text>
        <IconButton iconName="close" onClick={handleClose} />
      </header>
      <div className="flex flex-col gap-y-5 px-14 py-8">
        {/* form */}
        <div className="w-full rounded border-2 border-dashed border-marble-500 bg-secondary-50 px-5 py-4">
          Updating {agent.name} will affect everyone using the assistant
        </div>
        <Button
          className="self-end"
          splitIcon="check-mark"
          onClick={handleUpdate}
          disabled={!canSubmit}
        >
          Update
        </Button>
      </div>
    </Transition>
  );
};
