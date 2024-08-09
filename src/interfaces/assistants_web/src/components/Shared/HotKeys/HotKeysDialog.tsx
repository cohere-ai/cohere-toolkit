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
import { Fragment, useMemo, useState } from 'react';

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
          <div className="transition-o`pacity fixed inset-0 bg-volcanic-300/20 backdrop-blur-sm" />
        </TransitionChild>

        <div className="fixed inset-0 flex items-center justify-center overflow-y-auto p-4">
          <TransitionChild
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0 scale-90"
            enterTo="opacity-100 scale-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100 scale-100"
            leaveTo="opacity-0 scale-90"
          >
            <DialogPanel className="relative flex w-full flex-col rounded-lg bg-marble-1000 md:w-modal dark:bg-volcanic-200">
              <Combobox as="div" onChange={handleOnChange}>
                <div className="mb-4 px-6 pt-6">
                  <ComboboxInput
                    as={Input}
                    placeholder="Type a command or search..."
                    value={query}
                    onChange={(event) => setQuery(event.target.value)}
                    onKeyDown={(event: React.KeyboardEvent<HTMLInputElement>) => {
                      if (event.key === 'Escape') {
                        close();
                      }
                    }}
                    autoFocus
                    className="border-none bg-transparent focus:bg-transparent dark:bg-transparent dark:focus:bg-transparent"
                  />
                  <hr className="border-t dark:border-volcanic-700" />
                </div>
                {filteredCustomActions.length > 0 && (
                  <ComboboxOptions className="my-4 max-h-72 space-y-6 overflow-y-auto" static>
                    <CommandActionGroup isOpen={isOpen} options={filteredCustomActions} />
                  </ComboboxOptions>
                )}
                {query === '' && <CommandActionGroup isOpen={isOpen} options={options} />}
                {query !== '' && filteredCustomActions.length === 0 && (
                  <Text className="py-14 text-center">No results for &quot;{query}&quot;</Text>
                )}
              </Combobox>
            </DialogPanel>
          </TransitionChild>
        </div>
      </Dialog>
    </Transition>
  );
};
