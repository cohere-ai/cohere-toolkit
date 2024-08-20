'use client';

import {
  Combobox,
  ComboboxInput,
  ComboboxOptions,
  Dialog,
  DialogPanel,
  Transition,
  TransitionChild,
} from '@headlessui/react';
import { Fragment, useEffect, useMemo, useState } from 'react';

import CommandActionGroup from '@/components/Shared/HotKeys/CommandActionGroup';
import { type HotKeyGroupOption } from '@/components/Shared/HotKeys/domain';
import { Input } from '@/components/Shared/Input';
import { Text } from '@/components/Shared/Text';

type Props = {
  isOpen: boolean;
  close: VoidFunction;
  options?: HotKeyGroupOption[];
};

export const HotKeysDialog: React.FC<Props> = ({ isOpen, close, options = [] }) => {
  const [query, setQuery] = useState('');

  const filteredCustomActions = useMemo(() => {
    if (query === '') return [];
    if (query === '?') return options;

    const queryWords = query.toLowerCase().split(' ');
    return options
      .map((action) => {
        return {
          ...action,
          quickActions: action.quickActions.filter((quickAction) => {
            const name = quickAction.name.toLowerCase();
            return queryWords.every((word) => name.includes(word));
          }),
        };
      })
      .filter((action) => action.quickActions.length > 0);
  }, [query, options]);

  const handleOnChange = (command: string | null) => {
    if (command !== null) {
      close();
    }
  };

  useEffect(() => {
    if (!isOpen) {
      setTimeout(() => setQuery(''), 300); // Delay to prevent flickering
    }
  }, [isOpen]);

  return (
    <Transition show={isOpen} as={Fragment} appear>
      <Dialog as="div" className="relative z-modal" onClose={close}>
        <TransitionChild
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-[#B3B3B3]/60 transition-opacity dark:bg-[#1C1C1C]/80" />
        </TransitionChild>

        <div className="fixed inset-0 flex items-center justify-center overflow-y-auto">
          <TransitionChild
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0 scale-90"
            enterTo="opacity-100 scale-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100 scale-100"
            leaveTo="opacity-0 scale-90"
          >
            <DialogPanel className="relative flex max-h-[80vh] w-full flex-col overflow-hidden rounded-lg bg-volcanic-950 dark:bg-volcanic-200 md:w-modal">
              <Combobox as="div" onChange={handleOnChange}>
                <ComboboxInput
                  as={Input}
                  placeholder="Find a command."
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  onKeyDown={(event: React.KeyboardEvent<HTMLInputElement>) => {
                    if (event.key === 'Escape') {
                      close();
                    }
                  }}
                  autoFocus
                  className="border-none bg-transparent px-6 py-0 pt-6 text-p-lg focus:bg-transparent dark:bg-transparent dark:focus:bg-transparent"
                />
                <hr className="mx-6 mb-3 mt-6 border-t border-volcanic-800 dark:border-volcanic-400" />
                <ComboboxOptions className="flex flex-col gap-y-6 overflow-y-auto" static>
                  {filteredCustomActions.length > 0 && (
                    <CommandActionGroup isOpen={isOpen} options={filteredCustomActions} />
                  )}
                  {query === '' && <CommandActionGroup isOpen={isOpen} options={options} />}
                  {query !== '' && filteredCustomActions.length === 0 && (
                    <Text className="p-6">No results for &quot;{query}&quot;</Text>
                  )}
                </ComboboxOptions>
              </Combobox>
            </DialogPanel>
          </TransitionChild>
        </div>
      </Dialog>
    </Transition>
  );
};
