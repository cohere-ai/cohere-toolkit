'use client';

import React, { useContext } from 'react';

import { CohereClient } from './client';

const CohereClientContext = React.createContext<CohereClient | null>(null);

interface Props {
  client?: CohereClient;
  children: React.ReactNode;
}

/**
 * A provider component for the CohereClient. Render this component at the top of your
 * component tree to make the client available to all components that use useCohereClient().
 */
export const CohereClientProvider: React.FC<Props> = ({ client, children }) => {
  if (!client) return null;
  return <CohereClientContext.Provider value={client}>{children}</CohereClientContext.Provider>;
};

/**
 * A hook that returns the CohereClientContext instance. This hook should only be used within a
 * CohereClientContext Provider.
 */
export const useCohereClient = () => {
  const client = useContext(CohereClientContext);

  if (!client) {
    throw new Error('No CohereClientContext set. Use CohereClientProvider to set one.');
  }

  return client;
};
