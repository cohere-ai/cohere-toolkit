import { Transition } from '@headlessui/react';
import { DehydratedState, QueryClient, dehydrate } from '@tanstack/react-query';
import { GetServerSideProps, NextPage } from 'next';
import { useRouter } from 'next/router';
import { useContext, useEffect } from 'react';

import { CohereClient } from '@/cohere-client';
import { AgentsList } from '@/components/Agents/AgentsList';
import { Layout, LeftSection, MainSection } from '@/components/Agents/Layout';
import Conversation from '@/components/Conversation';
import ConversationListPanel from '@/components/ConversationList/ConversationListPanel';
import { BannerContext } from '@/context/BannerContext';
import { useIsDesktop } from '@/hooks/breakpoint';
import { useListAllDeployments } from '@/hooks/deployments';
import { useExperimentalFeatures } from '@/hooks/experimentalFeatures';
import { appSSR } from '@/pages/_app';
import {
  useCitationsStore,
  useConversationStore,
  useParamsStore,
  useSettingsStore,
} from '@/stores';
import { cn } from '@/utils';

type Props = {
  reactQueryState: DehydratedState;
};

const AgentsPage: NextPage<Props> = () => {
  const {
    conversation: { id },
    resetConversation,
  } = useConversationStore();
  const {
    settings: { isConvListPanelOpen, isMobileConvListPanelOpen },
  } = useSettingsStore();
  const router = useRouter();
  const agentId = router.query.assistantId as string | undefined;
  const isDesktop = useIsDesktop();
  const isMobile = !isDesktop;

  const { resetCitations } = useCitationsStore();
  const {
    params: { deployment },
    setParams,
    resetFileParams,
  } = useParamsStore();
  const { data: allDeployments } = useListAllDeployments();
  const { data: experimentalFeatures } = useExperimentalFeatures();
  const isLangchainModeOn = !!experimentalFeatures?.USE_EXPERIMENTAL_LANGCHAIN;
  const { setMessage } = useContext(BannerContext);

  useEffect(() => {
    resetConversation();
    resetCitations();
    resetFileParams();
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
        <AgentsList />
      </LeftSection>
      <MainSection>
        <div className="flex h-full">
          <Transition
            as="main"
            show={(isMobileConvListPanelOpen && isMobile) || (isConvListPanelOpen && isDesktop)}
            enterFrom="translate-x-full lg:translate-x-0 lg:w-0"
            enterTo="translate-x-0 lg:w-[300px]"
            leaveFrom="translate-x-0 lg:w-[300px]"
            leaveTo="translate-x-full lg:translate-x-0 lg:w-0"
            className={cn(
              'z-main-section flex flex-grow lg:min-w-0',
              'absolute h-full w-full lg:static lg:h-auto',
              'border-0 border-marble-400 md:border-r',
              'transition-[transform, width] duration-500 ease-in-out'
            )}
          >
            <ConversationListPanel />
          </Transition>
          <Transition
            as="div"
            show={isDesktop || !isMobileConvListPanelOpen}
            enterFrom="-translate-x-full"
            enterTo="translate-x-0"
            leaveFrom="translate-x-0"
            leaveTo="-translate-x-full"
            className={cn(
              'flex min-w-0 flex-grow flex-col',
              'transition-transform duration-500 ease-in-out'
            )}
          >
            <Conversation conversationId={id} agentId={agentId} startOptionsEnabled />
          </Transition>
        </div>
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
