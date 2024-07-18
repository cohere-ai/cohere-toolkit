'use client';

import { Dialog, Transition } from '@headlessui/react';
import React, { Fragment, PropsWithChildren } from 'react';

import { cn } from '@/utils';

type Props = PropsWithChildren<{
  isOpen: boolean;
  close: VoidFunction;
  className?: string;
}>;

export const LongPressMenu: React.FC<Props> = ({ isOpen, close, children, className }) => {
  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className={cn('relative z-modal', className)} onClose={close}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-300"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-volcanic-100/30" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-end justify-center px-2 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 translate-y-1/2"
              enterTo="opacity-100 translate-y-0"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 translate-y-0"
              leaveTo="opacity-0 translate-y-1/2"
            >
              <Dialog.Panel
                className={cn(
                  'w-full transform select-none overflow-hidden rounded-t-xl p-6 transition-all',
                  'bg-marble-1000'
                )}
              >
                {children}
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
};
