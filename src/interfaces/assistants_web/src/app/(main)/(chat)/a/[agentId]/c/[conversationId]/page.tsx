import { HydrationBoundary, QueryClient, dehydrate } from '@tanstack/react-query';
import { NextPage } from 'next';

import Chat from '@/app/(main)/(chat)/Chat';
import { getCohereServerClient } from '@/server/cohereServerClient';

type Props = {
  params: {
    agentId: string;
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
      queryKey: ['agent', params.agentId],
      queryFn: async () => cohereServerClient.getAgent(params.agentId),
    }),
  ]);

  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <Chat conversationId={params.conversationId} agentId={params.agentId} />
    </HydrationBoundary>
  );
};

export default Page;
