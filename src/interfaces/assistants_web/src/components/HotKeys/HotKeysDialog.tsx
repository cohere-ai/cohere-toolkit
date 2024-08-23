'use client';

import {
  Combobox,
  ComboboxOptions,
  Dialog,
  DialogPanel,
  Transition,
  TransitionChild,
} from '@headlessui/react';
import { Fragment, useEffect, useMemo, useState } from 'react';

import {
  CommandActionGroup,
  CustomHotKey,
  type HotKeyGroupOption,
  HotKeysDialogInput,
} from '@/components/HotKeys';
import { Text } from '@/components/UI';
import { cn } from '@/utils';

type Props = {
  isOpen: boolean;
  close: VoidFunction;
  options?: HotKeyGroupOption[];
};

export const HotKeysDialog: React.FC<Props> = ({ isOpen, close, options = [] }) => {
  const [query, setQuery] = useState('');
  const [customView, setCustomView] = useState<string | null>(null);

  const View = useMemo(() => {
    const option = options.find((option) =>
      option.quickActions.some((action) => action.name === customView)
    );
    return option?.quickActions.find((action) => action.name === customView)?.customView;
  }, [customView, options]);

  const filteredCustomActions = useMemo(() => {
    if (query === '') return [];
    if (query === '?') return options;
    if (query === '$') {
      setCustomView('Search');
      return [];
    }

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

  const handleOnChange = (hotkey?: CustomHotKey) => {
    if (hotkey) {
      if (hotkey.closeDialogOnRun) {
        close();
      }
      hotkey.action?.();
      if (!!hotkey.customView) {
        setCustomView(hotkey.name);
      }
    }
  };

  useEffect(() => {
    if (!isOpen) {
      // Delay to prevent flickering
      setTimeout(() => {
        setCustomView(null);
        setQuery('');
      }, 300);
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
            <DialogPanel>
              <Combobox
                as="div"
                onChange={handleOnChange}
                immediate
                className={cn(
                  'relative flex max-h-[480px] w-full flex-col overflow-y-hidden rounded-lg bg-volcanic-950 transition-all duration-300 dark:bg-volcanic-200 md:w-modal'
                )}
              >
                {View ? (
                  <View isOpen={isOpen} close={close} onBack={() => setCustomView(null)} />
                ) : (
                  <>
                    <HotKeysDialogInput
                      value={query}
                      setValue={setQuery}
                      close={close}
                      placeholder="Find a command"
                    />
                    <ComboboxOptions className="mb-3 flex flex-col gap-y-6 overflow-y-auto" static>
                      {filteredCustomActions.length > 0 && (
                        <CommandActionGroup isOpen={isOpen} options={filteredCustomActions} />
                      )}
                      {query === '' && <CommandActionGroup isOpen={isOpen} options={options} />}
                      {query !== '' && filteredCustomActions.length === 0 && (
                        <Text className="p-6">No results for &quot;{query}&quot;</Text>
                      )}
                    </ComboboxOptions>
                  </>
                )}
              </Combobox>
            </DialogPanel>
          </TransitionChild>
        </div>
      </Dialog>
    </Transition>
  );
};
