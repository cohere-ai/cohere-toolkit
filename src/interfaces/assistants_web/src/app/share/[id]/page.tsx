'use client';

import { NextPage } from 'next';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';

import { Document } from '@/cohere-client';
import { ReadOnlyConversation } from '@/components/ReadOnlyConversation';
import { Icon, Spinner, Text } from '@/components/Shared';
import { DEFAULT_CONVERSATION_NAME } from '@/constants';
import { useGetSnapshotByLinkId } from '@/hooks/snapshots';
import { useCitationsStore } from '@/stores';
import {
  UserOrBotMessage,
  createStartEndKey,
  isShareLinkExpiredError,
  mapHistoryToMessages,
} from '@/utils';

const ShareConversationPage: NextPage = () => {
  const params = useParams();
  const linkId = params.id as string;
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
      <div className="flex min-h-[100vh] w-full items-center justify-center dark:bg-volcanic-100">
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
    <div className="flex min-h-[100vh] w-full flex-col items-center justify-center gap-2 px-6 md:px-0 dark:bg-volcanic-100">
      {content}
    </div>
  );
};

export default ShareConversationPage;
