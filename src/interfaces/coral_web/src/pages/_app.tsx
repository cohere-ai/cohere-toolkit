import {
  DehydratedState,
  HydrationBoundary,
  QueryClient,
  QueryClientProvider,
} from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import fetch from 'cross-fetch';
import type { AppProps } from 'next/app';

import { CohereClient, CohereClientProvider, Fetch } from '@/cohere-client';
import { ToastNotification } from '@/components/Shared';
import { WebManifestHead } from '@/components/Shared';
import { GlobalHead } from '@/components/Shared/GlobalHead';
import { ViewportFix } from '@/components/ViewportFix';
import { ContextStore } from '@/context';
import { env } from '@/env.mjs';
import { useLazyRef } from '@/hooks/lazyRef';
import '@/styles/main.css';

/**
 * Create a CohereAPIClient with the given access token.
 */
const makeCohereClient = () => {
  const apiFetch: Fetch = async (resource, config) => await fetch(resource, config);
  return new CohereClient({
    hostname: env.NEXT_PUBLIC_API_HOSTNAME,
    source: 'coral',
    fetch: apiFetch,
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
  const cohereClient = useLazyRef(() => makeCohereClient());
  const queryClient = useLazyRef(() => new QueryClient());

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
