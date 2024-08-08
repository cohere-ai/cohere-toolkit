'use client';

import { Combobox, Dialog, DialogPanel, Transition } from '@headlessui/react';
import { Fragment, useMemo, useState } from 'react';

import DialogNavigationKeys from '@/components/Shared/HotKeys/DialogNavigationKeys';
import QuickActions, { QuickAction } from '@/components/Shared/HotKeys/QuickActions';
import { Input } from '@/components/Shared/Input';
import { Text } from '@/components/Shared/Text';

type Props = {
  isOpen: boolean;
  close: VoidFunction;
  customActions?: QuickAction[];
};

export const HotKeysDialog: React.FC<Props> = ({ isOpen, close, customActions = [] }) => {
  const [query, setQuery] = useState('');

  const filteredCustomActions = useMemo(() => {
    if (query === '') return [];
    if (query === '?') return customActions;

    const queryWords = query.toLowerCase().split(' ');
    return customActions.filter((action) => {
      return queryWords.every((queryWord) => action.name.toLowerCase().includes(queryWord));
    });
  }, [query]);

  const handleOnChange = (command: string | null) => {
    if (command !== null) {
      close();
    }
  };

  return (
    <Transition.Root show={isOpen} as={Fragment} appear>
      <Dialog as="div" className="relative z-modal" onClose={close}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="transition-o`pacity fixed inset-0 bg-volcanic-300/20 backdrop-blur-sm" />
        </Transition.Child>

        <div className="fixed inset-0 flex items-start justify-center overflow-y-auto p-4">
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0 scale-90"
            enterTo="opacity-100 scale-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100 scale-100"
            leaveTo="opacity-0 scale-90"
          >
            <DialogPanel className="relative flex w-full flex-col rounded-lg bg-marble-1000 md:w-modal dark:bg-volcanic-200">
              <div className="p-6">
                <Combobox as="div" onChange={handleOnChange}>
                  <Combobox.Input
                    as={Input}
                    placeholder="Search"
                    value={query}
                    onChange={(event) => setQuery(event.target.value)}
                    onKeyDown={(event: React.KeyboardEvent<HTMLInputElement>) => {
                      if (event.key === 'Escape') {
                        close();
                      }
                    }}
                    autoFocus
                    className="mb-4"
                  />
                  {filteredCustomActions.length > 0 && (
                    <Combobox.Options className="mt-4 max-h-72 overflow-y-auto" static>
                      <QuickActions isOpen={isOpen} customActions={filteredCustomActions} />
                    </Combobox.Options>
                  )}
                  {query === '' && <QuickActions isOpen={isOpen} customActions={customActions} />}
                  {query !== '' && filteredCustomActions.length === 0 && (
                    <Text className="py-14 text-center">No results for &quot;{query}&quot;</Text>
                  )}
                </Combobox>
              </div>
              <DialogNavigationKeys />
            </DialogPanel>
          </Transition.Child>
        </div>
      </Dialog>
    </Transition.Root>
  );
};
