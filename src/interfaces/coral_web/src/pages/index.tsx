import { DehydratedState, QueryClient, dehydrate } from '@tanstack/react-query';
import { GetServerSideProps, NextPage } from 'next';
import { useEffect } from 'react';

import { CohereClient } from '@/cohere-client';
import Conversation from '@/components/Conversation';
import ConversationListPanel from '@/components/ConversationList/ConversationListPanel';
import { Layout, LayoutSection } from '@/components/Layout';
import { useListDeployments } from '@/hooks/deployments';
import { appSSR } from '@/pages/_app';
import { useCitationsStore, useConversationStore, useParamsStore } from '@/stores';

type Props = {
  reactQueryState: DehydratedState;
};

const ChatPage: NextPage<Props> = () => {
  const {
    conversation: { id },
    resetConversation,
  } = useConversationStore();
  const { resetCitations } = useCitationsStore();
  const {
    params: { deployment },
    setParams,
  } = useParamsStore();
  const { data: availableDeployments } = useListDeployments();

  useEffect(() => {
    resetConversation();
    resetCitations();
  }, []);

  useEffect(() => {
    if (!deployment && availableDeployments && availableDeployments?.length > 0) {
      setParams({ deployment: availableDeployments[0].name });
    }
  }, [deployment, availableDeployments]);

  return (
    <Layout>
      <LayoutSection.LeftDrawer>
        <ConversationListPanel />
      </LayoutSection.LeftDrawer>
      <LayoutSection.Main>
        <Conversation conversationId={id} welcomeMessageEnabled />
      </LayoutSection.Main>
    </Layout>
  );
};

export const getServerSideProps: GetServerSideProps = async () => {
  const deps = appSSR.initialize() as {
    queryClient: QueryClient;
    cohereClient: CohereClient;
  };

  await Promise.allSettled([
    deps.queryClient.prefetchQuery({
      queryKey: ['conversations'],
      queryFn: async () => {
        return (await deps.cohereClient.listConversations({})) ?? [];
      },
    }),
    deps.queryClient.prefetchQuery({
      queryKey: ['tools'],
      queryFn: async () => await deps.cohereClient.listTools({}),
    }),
    deps.queryClient.prefetchQuery({
      queryKey: ['deployments'],
      queryFn: async () => await deps.cohereClient.listDeployments(),
    }),
  ]);

  return {
    props: {
      appProps: {
        reactQueryState: dehydrate(deps.queryClient),
      },
    },
  };
};

export default ChatPage;
