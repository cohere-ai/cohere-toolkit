'use client';

import { Dialog, DialogPanel, DialogTitle, Transition, TransitionChild } from '@headlessui/react';
import React, { Fragment } from 'react';

import { Text } from '@/components/Shared';
import { cn } from '@/utils';

type ModalProps = {
  isOpen: boolean;
  title?: string;
  children?: React.ReactNode;
  onClose?: VoidFunction;
};

/**
 * A modal that appears centered on top of a fullscreen gray overlay.
 */
export const Modal: React.FC<ModalProps> = ({
  title = '',
  isOpen,
  children,
  onClose = () => {},
}) => {
  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog onClose={onClose} className={cn()}>
        <TransitionChild
          as={Fragment}
          enter="ease-out transition-opacity duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in transition-opacity duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div
            className="fixed inset-0 z-backdrop bg-volcanic-300/20 transition-opacity dark:bg-volcanic-100/80"
            aria-hidden="true"
          />
        </TransitionChild>

        {/* Full-screen container to center the panel */}
        <div className="fixed inset-0 z-modal flex items-center justify-center overflow-auto p-4">
          <TransitionChild
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0 scale-90"
            enterTo="opacity-100 scale-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100 scale-100"
            leaveTo="opacity-0 scale-90"
          >
            {/* Container to center the panel */}
            <div
              className={cn(
                'absolute top-0 flex min-h-full w-full items-center justify-center overflow-auto p-4 md:w-modal'
              )}
            >
              {children && (
                <DialogPanel
                  className={cn(
                    'h-fit max-h-modal overflow-y-auto rounded-lg border px-5 py-7 md:px-10 md:py-14',
                    'flex flex-col gap-y-8',
                    'border-marble-900 dark:border-volcanic-500',
                    'bg-mushroom-950 dark:bg-volcanic-200'
                  )}
                >
                  {title && (
                    <header>
                      {title && (
                        <DialogTitle as="div" className="flex-0 text-center">
                          <Text as="h5">{title}</Text>
                        </DialogTitle>
                      )}
                    </header>
                  )}
                  {children}
                </DialogPanel>
              )}
            </div>
          </TransitionChild>
        </div>
      </Dialog>
    </Transition>
  );
};
