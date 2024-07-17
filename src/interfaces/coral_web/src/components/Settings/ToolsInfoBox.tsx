'use client';

import { Transition } from '@headlessui/react';

import { Button, Text } from '@/components/Shared';
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
        Tools are functions that the model can access, such as searching Wikipedia or summarizing an
        uploaded PDF. Follow the documentation to add custom available tools.
        <br />
        <br />
        Tools can be turned on or off at any time in your conversation.
      </Text>
      <Button
        label={
          <Text styleAs="label" className="font-medium text-coral-300">
            Got it
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
