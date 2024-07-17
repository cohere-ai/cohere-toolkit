import { Transition } from '@headlessui/react';
import { QueryClient, dehydrate } from '@tanstack/react-query';
import { GetServerSideProps, NextPage } from 'next';
import { useContext, useEffect } from 'react';

import { CohereClient, Document, ManagedTool } from '@/cohere-client';
import { AgentsList } from '@/components/Agents/AgentsList';
import { ConnectDataModal } from '@/components/ConnectDataModal';
import Conversation from '@/components/Conversation';
import { ConversationError } from '@/components/ConversationError';
import ConversationListPanel from '@/components/ConversationList/ConversationListPanel';
import { AgentsLayout, Layout, LeftSection, MainSection } from '@/components/Layout';
import { ProtectedPage } from '@/components/ProtectedPage';
import { Spinner } from '@/components/Shared';
import { TOOL_PYTHON_INTERPRETER_ID } from '@/constants';
import { BannerContext } from '@/context/BannerContext';
import { ModalContext } from '@/context/ModalContext';
import { useAgent } from '@/hooks/agents';
import { useIsDesktop } from '@/hooks/breakpoint';
import { useConversation } from '@/hooks/conversation';
import { useListAllDeployments } from '@/hooks/deployments';
import { useExperimentalFeatures } from '@/hooks/experimentalFeatures';
import { useSlugRoutes } from '@/hooks/slugRoutes';
import { useListTools, useShowUnauthedToolsModal } from '@/hooks/tools';
import { appSSR } from '@/pages/_app';
import {
  useCitationsStore,
  useConversationStore,
  useParamsStore,
  useSettingsStore,
} from '@/stores';
import { OutputFiles } from '@/stores/slices/citationsSlice';
import { cn, createStartEndKey, mapHistoryToMessages } from '@/utils';
import { getSlugRoutes } from '@/utils/getSlugRoutes';
import { parsePythonInterpreterToolFields } from '@/utils/tools';

const Page: NextPage = () => {
  const { agentId, conversationId } = useSlugRoutes();
  const { setConversation } = useConversationStore();
  const {
    settings: { isConvListPanelOpen, isMobileConvListPanelOpen },
  } = useSettingsStore();

  const isDesktop = useIsDesktop();
  const isMobile = !isDesktop;

  const { addCitation, resetCitations, saveOutputFiles } = useCitationsStore();
  const {
    params: { deployment },
    setParams,
    resetFileParams,
  } = useParamsStore();
  const { show: showUnauthedToolsModal, onDismissed } = useShowUnauthedToolsModal();
  const { data: allDeployments } = useListAllDeployments();
  const { data: agent } = useAgent({ agentId });
  const { data: tools } = useListTools();
  const { data: experimentalFeatures } = useExperimentalFeatures();
  const isLangchainModeOn = !!experimentalFeatures?.USE_EXPERIMENTAL_LANGCHAIN;
  const isAgentsModeOn = !!experimentalFeatures?.USE_AGENTS_VIEW;

  const { setMessage } = useContext(BannerContext);
  const { open, close } = useContext(ModalContext);

  const {
    data: conversation,
    isLoading,
    isError,
    error,
  } = useConversation({
    conversationId: conversationId,
  });

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
    resetCitations();
    resetFileParams();

    const agentTools = (agent?.tools
      .map((name) => (tools ?? [])?.find((t) => t.name === name))
      .filter((t) => t !== undefined) ?? []) as ManagedTool[];
    setParams({
      tools: agentTools,
    });

    if (conversationId) {
      setConversation({ id: conversationId });
    }
  }, [conversationId, setConversation, resetCitations, agent, tools]);

  useEffect(() => {
    if (!conversation) return;

    const messages = mapHistoryToMessages(
      conversation?.messages?.sort((a, b) => a.position - b.position)
    );

    setConversation({ name: conversation.title, messages });

    let documentsMap: { [documentId: string]: Document } = {};
    let outputFilesMap: OutputFiles = {};

    (conversation?.messages ?? []).forEach((message) => {
      message.documents?.forEach((doc) => {
        const docId = doc.document_id ?? '';
        documentsMap[docId] = doc;

        const toolName = (doc.tool_name ?? '').toLowerCase();

        if (toolName === TOOL_PYTHON_INTERPRETER_ID) {
          const { outputFile } = parsePythonInterpreterToolFields(doc);

          if (outputFile) {
            outputFilesMap[outputFile.filename] = {
              name: outputFile.filename,
              data: outputFile.b64_data,
              documentId: docId,
            };
          }
        }
      });
      message.citations?.forEach((citation) => {
        const startEndKey = createStartEndKey(citation.start ?? 0, citation.end ?? 0);
        const documents = citation.document_ids?.map((id) => documentsMap[id]) ?? [];
        addCitation(message.generation_id ?? '', startEndKey, documents);
      });
    });

    saveOutputFiles(outputFilesMap);
  }, [conversation?.id, setConversation]);

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

  if (isAgentsModeOn) {
    return (
      <ProtectedPage>
        <AgentsLayout showSettingsDrawer>
          <LeftSection>
            <AgentsList />
          </LeftSection>
          <MainSection>
            <div className="flex h-full">
              <Transition
                as="section"
                appear
                show={(isMobileConvListPanelOpen && isMobile) || (isConvListPanelOpen && isDesktop)}
                enterFrom="translate-x-full lg:translate-x-0 lg:min-w-0 lg:max-w-0"
                enterTo="translate-x-0 lg:min-w-[300px] lg:max-w-[300px]"
                leaveFrom="translate-x-0 lg:min-w-[300px] lg:max-w-[300px]"
                leaveTo="translate-x-full lg:translate-x-0 lg:min-w-0 lg:max-w-0"
                className={cn(
                  'z-main-section flex lg:min-w-0',
                  'absolute h-full w-full lg:static lg:h-auto',
                  'border-0 border-marble-950 md:border-r',
                  'transition-[transform,min-width,max-width] duration-300 ease-in-out'
                )}
              >
                <ConversationListPanel agentId={agentId} />
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
                {isLoading ? (
                  <div className="flex h-full flex-grow flex-col items-center justify-center">
                    <Spinner />
                  </div>
                ) : isError ? (
                  <ConversationError error={error} />
                ) : (
                  <Conversation
                    conversationId={conversationId}
                    agentId={agentId}
                    startOptionsEnabled
                  />
                )}
              </Transition>
            </div>
          </MainSection>
        </AgentsLayout>
      </ProtectedPage>
    );
  }

  return (
    <ProtectedPage>
      <Layout>
        <LeftSection>
          <ConversationListPanel />
        </LeftSection>
        <MainSection>
          <Conversation conversationId={conversation?.id} startOptionsEnabled />
        </MainSection>
      </Layout>
    </ProtectedPage>
  );
};

export const getServerSideProps: GetServerSideProps = async (context) => {
  const deps = appSSR.initialize() as {
    queryClient: QueryClient;
    cohereClient: CohereClient;
  };

  const { conversationId, agentId } = getSlugRoutes(context.query.slug);

  const prefetchQueries = [
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
      queryFn: async () => await deps.cohereClient.listDeployments({}),
    }),
  ];

  prefetchQueries.push(
    deps.queryClient.prefetchQuery({
      queryKey: ['agent', agentId],
      queryFn: async () => {
        if (!agentId) {
          return await deps.cohereClient.getDefaultAgent();
        }
        return await deps.cohereClient.getAgent(agentId);
      },
    })
  );

  if (conversationId) {
    prefetchQueries.push(
      deps.queryClient.prefetchQuery({
        queryKey: ['conversation', conversationId],
        queryFn: async () => {
          const conversation = await deps.cohereClient.getConversation({
            conversationId,
          });
          // react-query useInfiniteQuery expected response shape
          return { conversation };
        },
      })
    );
  }

  await Promise.allSettled(prefetchQueries);

  return {
    props: {
      appProps: {
        reactQueryState: dehydrate(deps.queryClient),
      },
    },
  };
};

export default Page;
