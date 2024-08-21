import { ComboboxOptions } from '@headlessui/react';

import { CommandActionGroup, HotKeysDialogInput } from '@/components/HotKeys';
import { useAssistantHotKeys } from '@/hooks/actions';

type Props = {
  close: VoidFunction;
  onBack: VoidFunction;
};

export const SwitchAssistants: React.FC<Props> = ({ close, onBack }) => {
  const assistantHotKeys = useAssistantHotKeys({ displayRecentAgentsInDialog: true });

  return (
    <>
      <HotKeysDialogInput value="Switch assistants" readOnly close={close} onBack={onBack} />
      <ComboboxOptions className="flex flex-col gap-y-6 overflow-y-auto pb-3" static>
        <CommandActionGroup isOpen options={assistantHotKeys} />
      </ComboboxOptions>
    </>
  );
};
