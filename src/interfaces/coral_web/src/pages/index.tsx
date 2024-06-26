import { Transition } from '@headlessui/react';
import { QueryClient, dehydrate } from '@tanstack/react-query';
import { GetServerSideProps, NextPage } from 'next';
import { useContext, useEffect } from 'react';

import { CohereClient } from '@/cohere-client';
import { AgentsList } from '@/components/Agents/AgentsList';
import { ConnectDataModal } from '@/components/Agents/ConnectDataModal';
import { Layout, LeftSection, MainSection } from '@/components/Agents/Layout';
import Conversation from '@/components/Conversation';
import ConversationListPanel from '@/components/ConversationList/ConversationListPanel';
import { BannerContext } from '@/context/BannerContext';
import { ModalContext } from '@/context/ModalContext';
import { useIsDesktop } from '@/hooks/breakpoint';
import { useExperimentalFeatures } from '@/hooks/experimentalFeatures';
import { useShowUnauthedToolsModal } from '@/hooks/tools';
import { appSSR } from '@/pages/_app';
import { useSettingsStore } from '@/stores';
import { cn } from '@/utils';
import { getSlugRoutes } from '@/utils/getSlugRoutes';

const DefaultAgentPage: NextPage = () => {
  const {
    settings: { isConvListPanelOpen, isMobileConvListPanelOpen },
  } = useSettingsStore();
  const isDesktop = useIsDesktop();
  const isMobile = !isDesktop;

  const { data: experimentalFeatures } = useExperimentalFeatures();
  const isLangchainModeOn = !!experimentalFeatures?.USE_EXPERIMENTAL_LANGCHAIN;
  const { show: showUnauthedToolsModal, onDismissed } = useShowUnauthedToolsModal();
  const { setMessage } = useContext(BannerContext);
  const { open, close } = useContext(ModalContext);

  useEffect(() => {
    if (showUnauthedToolsModal) {
      open({
        title: 'Connect your data',
        content: (
          <ConnectDataModal
            onClose={() => {
              onDismissed();
              close();
            }}
          />
        ),
      });
    }
  }, [showUnauthedToolsModal]);

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
            as="section"
            show={(isMobileConvListPanelOpen && isMobile) || (isConvListPanelOpen && isDesktop)}
            enterFrom="translate-x-full lg:translate-x-0 lg:w-0"
            enterTo="translate-x-0 lg:w-[300px]"
            leaveFrom="translate-x-0 lg:w-[300px]"
            leaveTo="translate-x-full lg:translate-x-0 lg:w-0"
            className={cn(
              'z-main-section flex lg:min-w-0',
              'absolute h-full w-full lg:static lg:h-auto',
              'border-0 border-marble-400 md:border-r',
              'transition-[transform, width] duration-500 ease-in-out'
            )}
          >
            <ConversationListPanel />
          </Transition>
          <Transition
            as="main"
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
            <Conversation startOptionsEnabled />
          </Transition>
        </div>
      </MainSection>
    </Layout>
  );
};

export const getServerSideProps: GetServerSideProps = async (context) => {
  const deps = appSSR.initialize() as {
    queryClient: QueryClient;
    cohereClient: CohereClient;
  };

  const { conversationId, agentId } = getSlugRoutes(context.query.slug);

  await Promise.allSettled([
    deps.queryClient.prefetchQuery({
      queryKey: ['agent', agentId],
      queryFn: async () => {
        if (!agentId) return;
        return await deps.cohereClient.getAgent(agentId);
      },
    }),
    deps.queryClient.prefetchQuery({
      queryKey: ['conversation', conversationId],
      queryFn: async () => {
        if (!conversationId) return;
        const conversation = await deps.cohereClient.getConversation({
          conversationId,
        });
        // react-query useInfiniteQuery expected response shape
        return { conversation };
      },
    }),
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

export default DefaultAgentPage;
