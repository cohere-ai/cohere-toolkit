import { HydrationBoundary, QueryClient, dehydrate } from '@tanstack/react-query';
import { NextPage } from 'next';

import Chat from '@/app/(main)/(chat)/Chat';
import { useGetDefaultAgent } from '@/hooks';

const Page: NextPage = async () => {
  const queryClient = new QueryClient();
  const defaultAgent = useGetDefaultAgent();

  await queryClient.prefetchQuery({
    queryKey: ['agent', null],
    queryFn: async () => defaultAgent,
  });

  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <Chat />
    </HydrationBoundary>
  );
};

export default Page;
