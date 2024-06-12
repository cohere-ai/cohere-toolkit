import { DehydratedState, QueryClient, dehydrate } from '@tanstack/react-query';
import { GetServerSideProps, NextPage } from 'next';
import { useContext, useEffect } from 'react';

import { CohereClient } from '@/cohere-client';
import { Layout, LeftSection, MainSection } from '@/components/Agents/Layout';
import { LeftPanel } from '@/components/Agents/LeftPanel';
import Conversation from '@/components/Conversation';
import { BannerContext } from '@/context/BannerContext';
import { useListAllDeployments } from '@/hooks/deployments';
import { useExperimentalFeatures } from '@/hooks/experimentalFeatures';
import { appSSR } from '@/pages/_app';
import { useCitationsStore, useConversationStore, useParamsStore } from '@/stores';

type Props = {
  reactQueryState: DehydratedState;
};

const AgentsPage: NextPage<Props> = () => {
  const {
    conversation: { id },
    resetConversation,
  } = useConversationStore();
  const { resetCitations } = useCitationsStore();
  const {
    params: { deployment },
    setParams,
  } = useParamsStore();
  const { data: allDeployments } = useListAllDeployments();
  const { data: experimentalFeatures } = useExperimentalFeatures();
  const isLangchainModeOn = !!experimentalFeatures?.USE_EXPERIMENTAL_LANGCHAIN;
  const { setMessage } = useContext(BannerContext);

  useEffect(() => {
    resetConversation();
    resetCitations();
  }, []);

  useEffect(() => {
    if (!deployment && allDeployments) {
      const firstAvailableDeployment = allDeployments.find((d) => d.is_available);
      if (firstAvailableDeployment) {
        setParams({ deployment: firstAvailableDeployment.name });
      }
    }
  }, [deployment, allDeployments]);

  useEffect(() => {
    if (!isLangchainModeOn) return;
    setMessage('You are using an experimental langchain multihop flow. There will be bugs.');
  }, [isLangchainModeOn]);

  return (
    <Layout>
      <LeftSection>
        <LeftPanel />
      </LeftSection>
      <MainSection>
        <Conversation conversationId={id} startOptionsEnabled />
      </MainSection>
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

export default AgentsPage;
