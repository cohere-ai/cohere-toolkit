import { ComboboxOption } from '@headlessui/react';
import { useHotkeys } from 'react-hotkeys-hook';

import { type QuickAction } from '@/components/Shared/HotKeys/domain';
import { Text } from '@/components/Shared/Text';
import { useOS } from '@/hooks/os';

interface Props extends QuickAction {
  isOpen: boolean;
}

export const CommandAction: React.FC<Props> = ({ name, commands, action, isOpen }) => {
  const os = useOS();

  useHotkeys(
    commands,
    (e) => {
      if (!isOpen) return;
      e.preventDefault();
      action();
    },
    {
      enableOnFormTags: true,
    },
    [isOpen, action]
  );

  const formatCommand = () => {
    if (commands.length === 0) return '';
    const [command] = commands;
    return command
      .split('+')
      .map((key) => {
        if (key === 'ctrl') return os === 'macOS' ? '⌘' : 'Ctrl';
        if (key === 'meta') return os === 'macOS' ? '⌘' : 'Win';
        if (key === 'alt') return os === 'macOS' ? 'Option' : 'Alt';
        if (key === 'shift') return 'Shift';
        if (key === 'backspace') return 'Backspace';
        return key.toUpperCase();
      })
      .join(' + ');
  };
  return (
    <>
      <ComboboxOption
        key={name}
        value={action}
        className="flex select-none items-center p-4 data-[focus]:bg-green-500 data-[focus]:text-white data-[focus]:dark:bg-volcanic-400"
      >
        <Text className="mx-3 flex w-full items-center justify-between">
          <Text className="flex-auto truncate">{name}</Text>
          <kbd className="font-code">{formatCommand()}</kbd>
        </Text>
      </ComboboxOption>
    </>
  );
};
