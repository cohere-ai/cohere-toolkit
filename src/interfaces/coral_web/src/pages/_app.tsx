import { useLocalStorageValue } from '@react-hookz/web';
import {
  DehydratedState,
  HydrationBoundary,
  QueryCache,
  QueryClient,
  QueryClientProvider,
} from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import fetch from 'cross-fetch';
import type { AppProps } from 'next/app';
import { useRouter } from 'next/router';

import {
  CohereClient,
  CohereClientProvider,
  CohereUnauthorizedError,
  Fetch,
} from '@/cohere-client';
import { ToastNotification } from '@/components/Shared';
import { WebManifestHead } from '@/components/Shared';
import { GlobalHead } from '@/components/Shared/GlobalHead';
import { ViewportFix } from '@/components/ViewportFix';
import { LOCAL_STORAGE_KEYS } from '@/constants';
import { ContextStore } from '@/context';
import { env } from '@/env.mjs';
import { useLazyRef } from '@/hooks/lazyRef';
import '@/styles/main.css';

/**
 * Create a CohereAPIClient with the given access token.
 */
const makeCohereClient = (authToken?: string) => {
  const apiFetch: Fetch = async (resource, config) => await fetch(resource, config);
  return new CohereClient({
    hostname: env.NEXT_PUBLIC_API_HOSTNAME,
    fetch: apiFetch,
    authToken,
  });
};

/**
 * Page components must return a value satisfying this type in `getServerSideProps`.
 */
export type PageAppProps = { appProps?: { reactQueryState: DehydratedState } };

export const appSSR = {
  initialize: () => {
    const queryClient = new QueryClient();
    const cohereClient = makeCohereClient();
    return { queryClient, cohereClient };
  },
};

type Props = AppProps<PageAppProps>;

const App: React.FC<Props> = ({ Component, pageProps, ...props }) => {
  const { value: authToken, remove: clearAuthToken } = useLocalStorageValue(
    LOCAL_STORAGE_KEYS.authToken,
    {
      defaultValue: undefined,
    }
  );
  const router = useRouter();
  const cohereClient = useLazyRef(() => makeCohereClient(authToken || undefined));
  const queryClient = useLazyRef(
    () =>
      new QueryClient({
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

  const reactQueryState = pageProps.appProps?.reactQueryState;
  if (!reactQueryState && !['/404', '/500', '/_error', '/_ping'].includes(props.router.route)) {
    // Ensure every page calls `appSSR.getAppProps`, except for 404, 500, _ping and _error pages which cannot
    // use `getServerSideProps`.
    throw new Error('reactQueryState is undefined.');
  }

  return (
    <CohereClientProvider client={cohereClient}>
      <QueryClientProvider client={queryClient}>
        <HydrationBoundary state={reactQueryState}>
          <ContextStore>
            <ViewportFix />
            <GlobalHead />
            <WebManifestHead />
            <ToastNotification />
            <ReactQueryDevtools />
            <Component {...pageProps} />
          </ContextStore>
        </HydrationBoundary>
      </QueryClientProvider>
    </CohereClientProvider>
  );
};

export default App;
