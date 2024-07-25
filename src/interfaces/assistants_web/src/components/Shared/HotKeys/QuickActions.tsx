'use client';

import { Combobox } from '@headlessui/react';
import { useHotkeys } from 'react-hotkeys-hook';

import { Text } from '@/components/Shared';
import { useOS } from '@/hooks/os';
import { cn } from '@/utils';

export type QuickAction = {
  name: string;
  commands: string[];
  action: () => void;
};

type QuickActionsProps = {
  isOpen: boolean;
  customActions?: QuickAction[];
};

const QuickActions: React.FC<QuickActionsProps> = ({ isOpen, customActions = [] }) => {
  return customActions.map((action) => (
    <QuickAction key={action.name} isOpen={isOpen} {...action} />
  ));
};

interface QuickActionProps extends QuickAction {
  isOpen: boolean;
}

const QuickAction: React.FC<QuickActionProps> = ({ name, commands, action, isOpen }) => {
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
    <Combobox.Option
      key={name}
      value={action}
      className={({ active }) =>
        cn('flex select-none items-center rounded-lg py-2', active && 'bg-green-600 text-white')
      }
    >
      {({ active }) => (
        <Text className="mx-3 flex w-full items-center justify-between">
          <Text className="flex-auto truncate">{name}</Text>
          <span
            className={cn({
              'text-white': active,
            })}
          >
            <kbd className="font-code">{formatCommand()}</kbd>
          </span>
        </Text>
      )}
    </Combobox.Option>
  );
};

export default QuickActions;
