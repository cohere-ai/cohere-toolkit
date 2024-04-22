import React, { PropsWithChildren, createContext, useState } from 'react';

import { Modal } from '@/components/Shared';

type ModalKind = React.ComponentProps<typeof Modal>['kind'];
interface OpenParams {
  title?: React.ReactNode;
  content?: React.ReactNode | React.FC;
  kind?: ModalKind;
}

export type OpenFunction = (params: OpenParams) => void;
export type CloseFunction = () => void;

interface Context {
  isOpen: boolean;
  title?: React.ReactNode;
  open: OpenFunction;
  close: CloseFunction;
  content: React.ReactNode | React.FC;
  kind?: ModalKind;
}

/**
 * This hook stores the metadata of the currently open modal. It is used to help open Modals through the Context API.
 */
const useModal = (): Context => {
  const [isOpen, setIsOpen] = useState(false);
  const [title, setTitle] = useState<React.ReactNode | undefined>(undefined);
  const [content, setContent] = useState<React.ReactNode | React.FC>(undefined);
  const [kind, setModalKind] = useState<ModalKind>('default');

  const open = ({ title, content, kind }: OpenParams) => {
    setIsOpen(true);
    setModalKind(kind);
    setTitle(title);
    setContent(content);
  };

  const close = () => {
    setIsOpen(false);
  };

  return { isOpen, open, close, content, title, kind };
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
});

const ModalProvider: React.FC<PropsWithChildren> = ({ children }) => {
  const { isOpen, title, open, close, content, kind } = useModal();

  return (
    <ModalContext.Provider value={{ isOpen, title, open, close, content }}>
      <>{children}</>
      <Modal title={title} isOpen={isOpen} onClose={close} kind={kind}>
        <>{content}</>
      </Modal>
    </ModalContext.Provider>
  );
};

export { ModalContext, ModalProvider };
