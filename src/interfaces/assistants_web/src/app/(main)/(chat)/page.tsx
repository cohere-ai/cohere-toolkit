import { HydrationBoundary, QueryClient, dehydrate } from '@tanstack/react-query';
import { NextPage } from 'next';

import Chat from '@/app/(main)/(chat)/Chat';
import { DEFAULT_AGENT_ID } from '@/constants';
import { getCohereServerClient } from '@/server/cohereServerClient';

const Page: NextPage = async () => {
  const queryClient = new QueryClient();
  const cohereServerClient = getCohereServerClient();

  await queryClient.prefetchQuery({
    queryKey: ['agent', DEFAULT_AGENT_ID],
    queryFn: () => cohereServerClient.getDefaultAgent(),
  });

  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <Chat />
    </HydrationBoundary>
  );
};

export default Page;
