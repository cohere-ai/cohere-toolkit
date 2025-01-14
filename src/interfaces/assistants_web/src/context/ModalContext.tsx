'use client';

import React, { PropsWithChildren, createContext, useState } from 'react';

import { Modal } from '@/components/UI';

interface OpenParams {
  title?: string;
  content?: React.ReactNode;
  dialogPaddingClassName?: string;
}

export type OpenFunction = (params: OpenParams) => void;
export type CloseFunction = () => void;

interface Context {
  isOpen: boolean;
  title?: string;
  open: OpenFunction;
  close: CloseFunction;
  content: React.ReactNode;
  dialogPaddingClassName?: string;
}

/**
 * This hook stores the metadata of the currently open modal. It is used to help open Modals through the Context API.
 */
const useModal = (): Context => {
  const [isOpen, setIsOpen] = useState(false);
  const [title, setTitle] = useState<string | undefined>(undefined);
  const [content, setContent] = useState<React.ReactNode>(undefined);
  const [dialogPaddingClassName, setDialogPaddingClassName] = useState<string | undefined>(
    undefined
  );

  const open = ({ title, content, dialogPaddingClassName }: OpenParams) => {
    setIsOpen(true);
    setTitle(title);
    setContent(content);
    setDialogPaddingClassName(dialogPaddingClassName);
  };

  const close = () => {
    setIsOpen(false);
  };

  return { isOpen, open, close, content, title, dialogPaddingClassName };
};

/**
 * Allows us to open modals using the Context API. Usage e.g. below
 *
 * const { open } = useContext(ModalContext);
 * // with standard title
 * open({title: 'Alert!', content: <div>This is a warning!</div>});
 * // without standard title
 * open({content: <><h1>Custom header</h1><div>Custom content</div></>})
 */
const ModalContext = createContext<Context>({
  isOpen: false,
  title: '',
  open: () => {},
  close: () => {},
  content: undefined,
  dialogPaddingClassName: undefined,
});

const ModalProvider: React.FC<PropsWithChildren> = ({ children }) => {
  const { isOpen, title, open, close, content, dialogPaddingClassName } = useModal();

  return (
    <ModalContext.Provider value={{ isOpen, title, open, close, content, dialogPaddingClassName }}>
      <>{children}</>
      <Modal
        title={title}
        isOpen={isOpen}
        onClose={close}
        dialogPaddingClassName={dialogPaddingClassName}
      >
        <>{content}</>
      </Modal>
    </ModalContext.Provider>
  );
};

export { ModalContext, ModalProvider };
