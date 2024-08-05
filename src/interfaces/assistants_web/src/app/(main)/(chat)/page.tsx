import { HydrationBoundary, QueryClient, dehydrate } from '@tanstack/react-query';
import { NextPage } from 'next';

import Chat from '@/app/(main)/(chat)/Chat';
import { DEFAULT_ASSISTANT_ID } from '@/constants';
import { getCohereServerClient } from '@/server/cohereClient';

const Page: NextPage = async () => {
  const cohereServerClient = getCohereServerClient();
  const queryClient = new QueryClient();

  await queryClient.prefetchQuery({
    queryKey: ['agent', DEFAULT_ASSISTANT_ID],
    queryFn: async () => cohereServerClient.getAgent(DEFAULT_ASSISTANT_ID),
  });
  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <Chat agentId={DEFAULT_ASSISTANT_ID} />
    </HydrationBoundary>
  );
};

export default Page;
