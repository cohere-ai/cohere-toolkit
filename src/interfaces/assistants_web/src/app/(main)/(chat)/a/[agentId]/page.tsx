import { HydrationBoundary, QueryClient, dehydrate } from '@tanstack/react-query';
import { NextPage } from 'next';

import Chat from '@/app/(main)/(chat)/Chat';
import { getCohereServerClient } from '@/server/cohereServerClient';

type Props = {
  params: {
    agentId: string;
  };
  searchParams: Record<string, string>;
};

const Page: NextPage<Props> = async ({ params }) => {
  const cohereServerClient = getCohereServerClient();
  const queryClient = new QueryClient();

  await queryClient.prefetchQuery({
    queryKey: ['agent', params.agentId],
    queryFn: async () => cohereServerClient.getAgent(params.agentId),
  });

  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <Chat agentId={params.agentId} />
    </HydrationBoundary>
  );
};

export default Page;
