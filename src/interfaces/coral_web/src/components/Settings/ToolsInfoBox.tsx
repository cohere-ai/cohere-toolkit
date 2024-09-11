'use client';

import { Transition } from '@headlessui/react';

import { Button, Text } from '@/components/Shared';
import { STRINGS } from '@/constants/strings';
import { useShowToolsInfoBox } from '@/hooks/ftux';
import { useSettingsStore } from '@/stores';

export const ToolsInfoBox: React.FC = () => {
  const {
    settings: { isConfigDrawerOpen },
  } = useSettingsStore();
  const { show, onDismissed } = useShowToolsInfoBox();

  return (
    <Transition
      show={show && isConfigDrawerOpen}
      appear
      as="article"
      role="note"
      className="flex flex-col gap-y-3 rounded bg-coral-950 px-3.5 py-3"
      leave="transition-opacity ease-in-out"
      leaveFrom="opacity-100"
      leaveTo="opacity-0"
    >
      <Text>
        {STRINGS.toolsDescriptionLong}
        <br />
        <br />
        {STRINGS.toolsOnOffDescription}
      </Text>
      <Button
        label={
          <Text styleAs="label" className="font-medium text-coral-300">
            {STRINGS.gotIt}
          </Text>
        }
        kind="secondary"
        animate={false}
        className="self-end"
        onClick={onDismissed}
      />
    </Transition>
  );
};
