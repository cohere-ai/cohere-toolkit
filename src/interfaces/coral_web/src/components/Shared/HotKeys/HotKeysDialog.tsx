'use client';

import { Combobox, Dialog, Transition } from '@headlessui/react';
import { Fragment } from 'react';

import DialogNavigationKeys from '@/components/Shared/HotKeys/DialogNavigationKeys';
import QuickActions, { QuickAction } from '@/components/Shared/HotKeys/QuickActions';

type ComboboxItem = {
  name: string;
  url: string;
  keywords: string[];
};

type Props = {
  isOpen: boolean;
  close: VoidFunction;
  customActions?: QuickAction[];
};

export const HotKeysDialog: React.FC<Props> = ({ isOpen, close, customActions = [] }) => {
  const handleGoTo = (url: string) => {
    close();
    if (!url) return;
    if (url.startsWith('http')) {
      window.open(url, '_blank');
      return;
    }

    window.location.href = url;
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
          <div className="fixed inset-0 bg-volcanic-300/20 backdrop-blur-sm transition-opacity" />
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
            <Dialog.Panel className="relative flex w-full max-w-modal-xs flex-col rounded-lg bg-marble-1000 md:max-w-modal xl:max-w-modal-lg">
              <div className="p-6">
                <Combobox as="div" onChange={(item: ComboboxItem) => handleGoTo(item.url)}>
                  <QuickActions isOpen={isOpen} onGoTo={handleGoTo} customActions={customActions} />
                </Combobox>
              </div>
              <DialogNavigationKeys />
            </Dialog.Panel>
          </Transition.Child>
        </div>
      </Dialog>
    </Transition.Root>
  );
};
