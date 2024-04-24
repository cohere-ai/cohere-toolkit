import { DehydratedState, QueryClient, dehydrate } from '@tanstack/react-query';
import { GetServerSideProps, NextPage } from 'next';
import { useRouter } from 'next/router';
import { useEffect } from 'react';

import { CohereClient, Document } from '@/cohere-client';
import Conversation from '@/components/Conversation';
import { ConversationError } from '@/components/ConversationError';
import ConversationListPanel from '@/components/ConversationList/ConversationListPanel';
import { Layout, LayoutSection } from '@/components/Layout';
import { Spinner } from '@/components/Shared';
import { useConversation } from '@/hooks/conversation';
import { useListDeployments } from '@/hooks/deployments';
import { appSSR } from '@/pages/_app';
import { useCitationsStore, useConversationStore, useParamsStore } from '@/stores';
import { createStartEndKey, mapHistoryToMessages } from '@/utils';

type Props = {
  reactQueryState: DehydratedState;
};

const ConversationPage: NextPage<Props> = () => {
  const router = useRouter();
  const {
    params: { deployment },
    setParams,
  } = useParamsStore();
  const { setConversation } = useConversationStore();
  const { addCitation, resetCitations } = useCitationsStore();

  const urlConversationId = Array.isArray(router.query.id)
    ? router.query.id[0]
    : (router.query.id as string);

  const {
    data: conversation,
    isLoading,
    isError,
    error,
  } = useConversation({ conversationId: urlConversationId });
  const { data: availableDeployments } = useListDeployments();

  useEffect(() => {
    resetCitations();

    if (urlConversationId) {
      setConversation({ id: urlConversationId });
    }
  }, [urlConversationId, setConversation, resetCitations]);

  useEffect(() => {
    if (!conversation) return;

    const messages = mapHistoryToMessages(
      conversation?.messages?.sort((a, b) => a.position - b.position)
    );
    setConversation({ name: conversation.title, messages });
  }, [conversation?.id, setConversation]);

  useEffect(() => {
    if (!deployment && availableDeployments && availableDeployments?.length > 0) {
      setParams({ deployment: availableDeployments[0].name });
    }
  }, [deployment]);

  useEffect(() => {
    let documentsMap: { [documentId: string]: Document } = {};
    (conversation?.messages ?? []).forEach((message) => {
      documentsMap =
        message.documents?.reduce<{ [documentId: string]: Document }>(
          (idToDoc, doc) => ({ ...idToDoc, [doc.document_id ?? '']: doc }),
          {}
        ) ?? {};
      message.citations?.forEach((citation) => {
        const startEndKey = createStartEndKey(citation.start ?? 0, citation.end ?? 0);
        const documents = citation.document_ids?.map((id) => documentsMap[id]) ?? [];
        addCitation(message.generation_id ?? '', startEndKey, documents);
      });
    });
  }, [conversation]);

  return (
    <Layout>
      <LayoutSection.LeftDrawer>
        <ConversationListPanel />
      </LayoutSection.LeftDrawer>

      <LayoutSection.Main>
        {isLoading ? (
          <div className="flex h-full flex-grow flex-col items-center justify-center">
            <Spinner />
          </div>
        ) : isError ? (
          <ConversationError error={error} />
        ) : (
          <Conversation conversationId={urlConversationId} />
        )}
      </LayoutSection.Main>
    </Layout>
  );
};

export const getServerSideProps: GetServerSideProps = async (context) => {
  const deps = appSSR.initialize() as {
    queryClient: QueryClient;
    cohereClient: CohereClient;
  };

  const conversationId = context.params?.id as string;

  await Promise.allSettled([
    deps.queryClient.prefetchQuery({
      queryKey: ['conversation', conversationId],
      queryFn: async () => {
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
        const conversations = await deps.cohereClient.listConversations({});
        return conversations;
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

export default ConversationPage;
