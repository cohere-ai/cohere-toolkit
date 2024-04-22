import { useContext } from 'react';

import { BannerContext, BannerProvider } from '@/context/BannerContext';
import { ModalContext, ModalProvider } from '@/context/ModalContext';

export const ContextStore: React.FC<{
  children: React.ReactNode;
}> = ({ children }) => {
  return (
    <ModalProvider>
      <BannerProvider>{children}</BannerProvider>
    </ModalProvider>
  );
};

export const useContextStore = () => {
  const modal = useContext(ModalContext);
  const banner = useContext(BannerContext);

  return { ...modal, banner };
};
