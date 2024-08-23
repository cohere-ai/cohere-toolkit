'use client';

import { ComboboxOptions } from '@headlessui/react';
import { useRouter } from 'next/navigation';

import {
  CommandAction,
  CommandActionGroup,
  HotKeysDialogInput,
  QuickAction,
} from '@/components/HotKeys';
import { useAssistantHotKeys } from '@/components/HotKeys/hotkeys/assistants';
import { Icon } from '@/components/UI';

type Props = {
  close: VoidFunction;
  isOpen: boolean;
  onBack: VoidFunction;
};

export const SwitchAssistants: React.FC<Props> = ({ isOpen, close, onBack }) => {
  const assistantHotKeys = useAssistantHotKeys({ displayRecentAgentsInDialog: true });
  const router = useRouter();

  const navigateToAssistants = () => {
    router.push('/discover');
  };

  const seeAllAssistantsAction: QuickAction = {
    name: 'See all assistants',
    label: (
      <span className="flex items-center gap-x-2">
        See all assistants
        <Icon name="arrow-right" />
      </span>
    ),
    action: navigateToAssistants,
    closeDialogOnRun: true,
    commands: [],
    registerGlobal: false,
  };

  return (
    <span className="mb-3">
      <HotKeysDialogInput value="Switch assistants" readOnly close={close} onBack={onBack} />
      <ComboboxOptions className="mb-3 flex flex-col gap-y-6 overflow-y-auto" static>
        <CommandActionGroup isOpen options={assistantHotKeys} />
      </ComboboxOptions>
      <hr className="mx-6 mb-3 border-t border-volcanic-800 dark:border-volcanic-400" />
      <CommandAction isOpen={isOpen} hotkey={seeAllAssistantsAction} />
    </span>
  );
};
