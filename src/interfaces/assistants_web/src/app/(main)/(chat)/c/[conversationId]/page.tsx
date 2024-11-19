import { HydrationBoundary, QueryClient, dehydrate } from '@tanstack/react-query';
import { NextPage } from 'next';

import Chat from '@/app/(main)/(chat)/Chat';
import { DEFAULT_AGENT_ID } from '@/constants';
import { getCohereServerClient } from '@/server/cohereServerClient';

type Props = {
  params: {
    conversationId: string;
  };
  searchParams: Record<string, string>;
};

const Page: NextPage<Props> = async ({ params }) => {
  const cohereServerClient = getCohereServerClient();
  const queryClient = new QueryClient();

  await Promise.all([
    queryClient.prefetchQuery({
      queryKey: ['conversation', params.conversationId],
      queryFn: async () =>
        cohereServerClient.getConversation({ conversationId: params.conversationId }),
    }),
    queryClient.prefetchQuery({
      queryKey: ['agent', DEFAULT_AGENT_ID],
      queryFn: () => cohereServerClient.getDefaultAgent(),
    }),
  ]);

  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <Chat conversationId={params.conversationId} />
    </HydrationBoundary>
  );
};

export default Page;
