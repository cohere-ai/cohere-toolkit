'use client';

import { QueryCache, QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useRouter } from 'next/navigation';
import { useCallback } from 'react';

import { setAuthToken, clearAuthToken } from '@/app/server.actions';
import {
  CohereClient,
  CohereClientProvider,
  CohereUnauthorizedError,
  Fetch,
} from '@/cohere-client';
import { ToastNotification, WebManifestHead } from '@/components/Shared';
import { GlobalHead } from '@/components/Shared/GlobalHead';
import { ViewportFix } from '@/components/ViewportFix';
import { ContextStore } from '@/context';
import { env } from '@/env.mjs';
import { useLazyRef } from '@/hooks/lazyRef';

const makeCohereClient = (authToken?: string, onAuthTokenUpdate?: (authToken?: string) => void) => {
  const apiFetch: Fetch = async (resource, config) => await fetch(resource, config);
  return new CohereClient({
    hostname: env.NEXT_PUBLIC_API_HOSTNAME,
    fetch: apiFetch,
    authToken,
    onAuthTokenUpdate,
  });
};


export const LayoutProviders: React.FC<React.PropsWithChildren<{ authToken?: string }>> = ({
  children,
  authToken,
}) => {

  const onAuthTokenUpdate = useCallback((newAuthToken: string | undefined) => {
    if (newAuthToken) {
      setAuthToken(newAuthToken);
    } else {
      clearAuthToken();
    }
  }, []);

  const router = useRouter();

  const cohereClient = useLazyRef(() => makeCohereClient(authToken || undefined, onAuthTokenUpdate));
  const queryClient = useLazyRef(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            retry: false,
          },
        },
        queryCache: new QueryCache({
          onError: (error) => {
            if (error instanceof CohereUnauthorizedError) {
              clearAuthToken();
              // Extract the current URL without query parameters or host.
              const currentPath = window.location.pathname + window.location.hash;
              router.push(`/login?redirect_uri=${encodeURIComponent(currentPath)}`);
            }
          },
        }),
      })
  );

  return (
    <CohereClientProvider client={cohereClient}>
      <QueryClientProvider client={queryClient}>
        <ContextStore>
          <ViewportFix />
          <GlobalHead />
          <WebManifestHead />
          <ToastNotification />
          <ReactQueryDevtools />
          {children}
        </ContextStore>
      </QueryClientProvider>
    </CohereClientProvider>
  );
};
