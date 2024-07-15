import { QueryClient, dehydrate } from '@tanstack/react-query';
import { GetServerSideProps, NextPage } from 'next';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';

import { CohereClient, Document } from '@/cohere-client';
import { ReadOnlyConversation } from '@/components/ReadOnlyConversation';
import { Icon, Spinner, Text } from '@/components/Shared';
import { DEFAULT_CONVERSATION_NAME, MAX_TIMEOUT_PREFETCH } from '@/constants';
import { useGetSnapshotByLinkId } from '@/hooks/snapshots';
import { appSSR } from '@/pages/_app';
import { useCitationsStore } from '@/stores';
import {
  UserOrBotMessage,
  createStartEndKey,
  isShareLinkExpiredError,
  mapHistoryToMessages,
} from '@/utils';

const ShareConversationPage: NextPage = () => {
  const router = useRouter();
  const linkId = router.query.id as string;
  const { isLoading, isError, data, error } = useGetSnapshotByLinkId(linkId);
  const { addCitation } = useCitationsStore();
  const [messages, setMessages] = useState<UserOrBotMessage[]>([]);

  useEffect(() => {
    if (!data) return;

    setMessages(mapHistoryToMessages(data.snapshot.messages));

    let documentsMap: { [documentId: string]: Document } = {};
    (data.snapshot.messages ?? []).forEach((message) => {
      message.documents?.forEach((doc) => {
        const docId = doc.document_id ?? '';
        documentsMap[docId] = doc;
      });
      message.citations?.forEach((citation) => {
        const startEndKey = createStartEndKey(citation.start ?? 0, citation.end ?? 0);
        const documents = citation.document_ids?.map((id) => documentsMap[id]) ?? [];
        addCitation(message.generation_id ?? '', startEndKey, documents);
      });
    });
  }, [data]);

  if (isLoading) {
    return (
      <div className="flex min-h-[100vh] w-full items-center justify-center">
        <Spinner />
      </div>
    );
  }

  const expired = isShareLinkExpiredError(error);
  let content: React.ReactNode = null;

  if (expired) {
    content = (
      <>
        <Icon name="warning" size="lg" className="mx-auto" />
        <Text className="max-w-sm text-center">
          This share link has expired. Please ask the owner to generate a new one. In the meantime,
          why not create your own{' '}
          <Link href="/" className="underline">
            conversation
          </Link>
          ?
        </Text>
      </>
    );
  } else if (isError) {
    content = (
      <>
        <Icon name="warning" size="lg" className="mx-auto" />
        <Text className="max-w-sm text-center">
          This share link is invalid. <br /> Why not create your own{' '}
          <Link href="/" className="underline">
            conversation
          </Link>
          ?
        </Text>
      </>
    );
  } else {
    content = (
      <ReadOnlyConversation
        title={data?.snapshot?.title ?? DEFAULT_CONVERSATION_NAME}
        messages={messages}
      />
    );
  }

  return (
    <div className="flex min-h-[100vh] w-full flex-col items-center justify-center gap-2 px-6 md:px-0">
      {content}
    </div>
  );
};

export const getServerSideProps: GetServerSideProps = async (context) => {
  const deps = appSSR.initialize() as {
    queryClient: QueryClient;
    cohereClient: CohereClient;
  };

  const linkId = context.params?.id as string;

  await Promise.allSettled([
    deps.queryClient.prefetchQuery({
      queryKey: ['listSnapshots'],
      queryFn: async () => {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), MAX_TIMEOUT_PREFETCH);
        try {
          await deps.cohereClient.listSnapshots();
        } catch (e) {
          console.error(e);
        } finally {
          clearTimeout(timeoutId);
        }
      },
    }),
    deps.queryClient.prefetchQuery({
      queryKey: ['snapshot', linkId],
      queryFn: async () => {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), MAX_TIMEOUT_PREFETCH);
        try {
          await deps.cohereClient.getSnapshot({ linkId });
        } catch (e) {
          console.error(e);
        } finally {
          clearTimeout(timeoutId);
        }
      },
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

export default ShareConversationPage;
