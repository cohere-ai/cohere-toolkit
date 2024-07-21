import React, { PropsWithChildren, createContext, useState } from 'react';

interface Context {
  message: React.ReactNode;
  setMessage: (message: React.ReactNode) => void;
}

const useBanner = (initialMessage?: string): Context => {
  const [message, setMessage] = useState<React.ReactNode>(initialMessage ?? '');

  return { message, setMessage };
};

const BannerContext = createContext<Context>({
  message: '',
  setMessage: () => {},
});

/**
 * @description Provider for the BannerContext.
 * Determines the message to display in the global banner.
 */
const BannerProvider: React.FC<PropsWithChildren> = ({ children }) => {
  const { message, setMessage } = useBanner();

  return (
    <BannerContext.Provider value={{ message, setMessage }}>
      <>{children}</>
    </BannerContext.Provider>
  );
};

export { BannerContext, BannerProvider };
