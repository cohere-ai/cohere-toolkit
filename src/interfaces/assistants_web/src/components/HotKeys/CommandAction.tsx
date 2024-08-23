'use client';

import { ComboboxOption } from '@headlessui/react';
import { useMemo } from 'react';
import { useHotkeys } from 'react-hotkeys-hook';

import { QuickAction } from '@/components/HotKeys';
import { Text } from '@/components/UI';
import { useOS } from '@/hooks';
import { cn } from '@/utils';

interface Props {
  hotkey: QuickAction;
  isOpen: boolean;
}

export const CommandAction: React.FC<Props> = ({ isOpen, hotkey }) => {
  const os = useOS();

  useHotkeys(
    hotkey.commands,
    (e) => {
      if (!isOpen) return;
      e.preventDefault();
      hotkey.action?.();
    },
    {
      enableOnFormTags: true,
    },
    [isOpen, hotkey.action]
  );

  const formattedCommands = useMemo(() => {
    if (hotkey.commands.length === 0) return [];
    const [command] = hotkey.commands;
    return command.split('+').map((key) => {
      if (key === 'meta') return os === 'macOS' ? '⌘' : 'win';
      if (key === 'alt') return os === 'macOS' ? '⌥' : 'alt';
      if (key === 'shift') return 'shift';
      if (key === 'backspace') return 'backspace';
      if (key.length === 1) return key.toUpperCase();
      return key;
    });
  }, [hotkey.commands, os]);

  return (
    <>
      <ComboboxOption
        key={hotkey.name}
        value={hotkey}
        className={cn(
          'flex select-none items-center px-6 py-4',
          'data-[focus]:bg-volcanic-900 data-[focus]:dark:bg-volcanic-300'
        )}
      >
        {({ focus }) => (
          <Text className="flex w-full items-center justify-between">
            <Text
              as="span"
              className={cn('flex-auto truncate', 'text-volcanic-500 dark:text-volcanic-800', {
                'text-volcanic-200 dark:text-marble-1000': focus,
              })}
            >
              {hotkey.label ?? hotkey.name}
            </Text>
            <span className="flex gap-x-1">
              {formattedCommands.map((key) => (
                <Text
                  as="kbd"
                  key={key}
                  styleAs="p-sm"
                  className={cn(
                    'rounded bg-volcanic-800 px-1.5 py-1',
                    'bg-volcanic-900 text-volcanic-500 dark:bg-volcanic-100 dark:text-volcanic-800',

                    {
                      'bg-volcanic-800 text-volcanic-200 dark:bg-volcanic-60 dark:text-marble-1000':
                        focus,
                    }
                  )}
                >
                  {key}
                </Text>
              ))}
            </span>
          </Text>
        )}
      </ComboboxOption>
    </>
  );
};
