import { HydrationBoundary, QueryClient, dehydrate } from '@tanstack/react-query';
import { NextPage } from 'next';

import Chat from '@/app/(main)/(chat)/Chat';
import { useGetDefaultAgent } from '@/hooks';
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
  const defaultAgent = useGetDefaultAgent();

  await Promise.all([
    queryClient.prefetchQuery({
      queryKey: ['conversation', params.conversationId],
      queryFn: async () =>
        cohereServerClient.getConversation({ conversationId: params.conversationId }),
    }),
    queryClient.prefetchQuery({
      queryKey: ['agent', null],
      queryFn: () => defaultAgent,
    }),
  ]);

  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <Chat conversationId={params.conversationId} />
    </HydrationBoundary>
  );
};

export default Page;
