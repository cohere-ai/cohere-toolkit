'use client';

import { Dialog, Transition } from '@headlessui/react';
import { cva } from 'class-variance-authority';
import React, { Fragment } from 'react';

import { Icon } from '@/components/Shared';
import { Text } from '@/components/Shared';
import { cn } from '@/utils';

type CloseButtonProps = {
  className?: string;
  onClose?: VoidFunction;
};

const CloseButton: React.FC<CloseButtonProps> = ({ onClose, className }) => (
  <button
    type="button"
    className={cn('group p-1 outline-none', className)}
    aria-label="Close"
    onClick={onClose}
  >
    <Icon name="close" size="md" />
  </button>
);

const dialogStyle = cva(['relative', 'z-modal'], {
  variants: {
    kind: {
      default: [],
      'coral-mobile-only': ['lg:hidden'],
      coral: [],
    },
  },
});

const panelStyle = cva(['relative', 'flex', 'w-full', 'flex-col', 'rounded-lg'], {
  variants: {
    kind: {
      default: [
        'max-w-modal',
        'gap-6',
        'bg-marble-1000',
        'py-10',
        'px-6',
        'md:gap-8',
        'md:px-10',
        'md:py-14',
        'lg:gap-10',
      ],
      'coral-mobile-only': ['max-w-modal', 'gap-2', 'bg-coral-900', 'p-3'],
      coral: ['max-w-modal', 'gap-2', 'bg-coral-900', 'p-3'],
    },
  },
});

const closeButtonStyle = cva([], {
  variants: {
    kind: {
      default: ['absolute', 'top-6', 'right-6'],
      'coral-mobile-only': ['absolute', 'top-1', 'right-2', 'text-volcanic-400'],
      coral: ['absolute', 'top-1', 'right-2', 'text-volcanic-700'],
    },
  },
});

const titleStyle = cva([], {
  variants: {
    kind: {
      default: ['px-8', 'text-center'],
      'coral-mobile-only': ['text-volcanic-400'],
      coral: ['text-volcanic-400'],
    },
  },
});

type ModalProps = {
  isOpen: boolean;
  title?: React.ReactNode;
  kind?: 'default' | 'coral-mobile-only' | 'coral';
  children?: React.ReactNode;
  hideCloseButton?: boolean;
  panelClassName?: string;
  onClose?: VoidFunction;
};

/**
 * A modal that appears centered on top of a fullscreen gray overlay.
 */
export const Modal: React.FC<ModalProps> = ({
  title = '',
  isOpen,
  kind = 'default',
  children,
  hideCloseButton = false,
  panelClassName,
  onClose = () => {},
}) => {
  const isCitation = kind === 'coral-mobile-only' || kind === 'coral';

  return (
    <Transition.Root appear show={isOpen} as={Fragment}>
      <Dialog onClose={onClose} className={cn(dialogStyle({ kind }))}>
        <Transition.Child
          as={Fragment}
          enter="ease-out transition-opacity duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in transition-opacity duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div
            className="fixed inset-0 bg-volcanic-300/20 backdrop-blur-sm transition-opacity"
            aria-hidden="true"
          />
        </Transition.Child>

        {/* Full-screen container to center the panel */}
        <div className="fixed inset-0 flex items-center justify-center overflow-auto p-4">
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0 scale-90"
            enterTo="opacity-100 scale-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100 scale-100"
            leaveTo="opacity-0 scale-90"
          >
            {/* Container to center the panel */}
            <div className="absolute top-0 flex min-h-full w-full items-center justify-center overflow-auto p-4">
              {children && (
                <Dialog.Panel className={cn(panelStyle({ kind, className: panelClassName }))}>
                  {!hideCloseButton && title && (
                    <header>
                      {!hideCloseButton && (
                        <CloseButton className={cn(closeButtonStyle({ kind }))} onClose={onClose} />
                      )}
                      {title && (
                        <Dialog.Title as="div" className="flex-0">
                          {typeof title === 'string' ? (
                            <Text
                              as="h5"
                              className={cn(titleStyle({ kind }))}
                              styleAs={isCitation ? 'label' : 'h5'}
                            >
                              {title}
                            </Text>
                          ) : (
                            title
                          )}
                        </Dialog.Title>
                      )}
                    </header>
                  )}
                  {children}
                </Dialog.Panel>
              )}
            </div>
          </Transition.Child>
        </div>
      </Dialog>
    </Transition.Root>
  );
};
