import { useContext } from 'react';

import { ModalContext, ModalProvider } from '@/context/ModalContext';

export const ContextStore: React.FC<{
  children: React.ReactNode;
}> = ({ children }) => {
  return (
    <ModalProvider>
      {children}
    </ModalProvider>
  );
};

export const useContextStore = () => {
  const modal = useContext(ModalContext);

  return { ...modal };
};
