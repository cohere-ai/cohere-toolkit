'use client';

import { NextPage } from 'next';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { PropsWithChildren, useEffect, useState } from 'react';

import { Document } from '@/cohere-client';
import { ReadOnlyConversation } from '@/components/ReadOnlyConversation';
import { Icon, Spinner, Text } from '@/components/Shared';
import { DEFAULT_CONVERSATION_NAME, TOOL_PYTHON_INTERPRETER_ID } from '@/constants';
import { useGetSnapshotByLinkId } from '@/hooks/snapshots';
import { useCitationsStore } from '@/stores';
import { OutputFiles } from '@/stores/slices/citationsSlice';
import {
  UserOrBotMessage,
  createStartEndKey,
  isShareLinkExpiredError,
  mapHistoryToMessages,
} from '@/utils';
import { parsePythonInterpreterToolFields } from '@/utils/tools';

const ShareConversationPage: NextPage = () => {
  const params = useParams();
  const linkId = params.id as string;
  const { isLoading, isError, data, error } = useGetSnapshotByLinkId(linkId);
  const { addCitation, saveOutputFiles } = useCitationsStore();
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

    const documents = data.snapshot.messages
      .map((message) => message.documents)
      .filter(Boolean)
      .flat();
    const outputFiles = documents
      .filter((doc) => doc.document_id.startsWith(TOOL_PYTHON_INTERPRETER_ID))
      .filter(Boolean)
      .reduce((acc, doc) => {
        const { outputFile } = parsePythonInterpreterToolFields(doc);
        if (outputFile) {
          acc[outputFile.filename] = {
            name: outputFile.filename,
            data: outputFile.b64_data,
            documentId: doc.document_id,
          };
        }
        return acc;
      }, {} as OutputFiles);
    saveOutputFiles(outputFiles);
  }, [data]);

  if (isLoading) {
    return (
      <div className="flex min-h-[100vh] w-full items-center justify-center dark:bg-volcanic-100">
        <Spinner />
      </div>
    );
  }

  const expired = isShareLinkExpiredError(error);

  if (expired) {
    return (
      <Wrapper>
        <Icon name="warning" size="lg" className="mx-auto" />
        <Text className="max-w-sm text-center">
          This share link has expired. Please ask the owner to generate a new one. In the meantime,
          why not create your own{' '}
          <Link href="/" className="underline">
            conversation
          </Link>
          ?
        </Text>
      </Wrapper>
    );
  }

  if (isError) {
    return (
      <Wrapper>
        <Icon name="warning" size="lg" className="mx-auto" />
        <Text className="max-w-sm text-center">
          This share link is invalid. <br /> Why not create your own{' '}
          <Link href="/" className="underline">
            conversation
          </Link>
          ?
        </Text>
      </Wrapper>
    );
  }

  return (
    <Wrapper>
      <ReadOnlyConversation
        title={data?.snapshot?.title ?? DEFAULT_CONVERSATION_NAME}
        messages={messages}
      />
    </Wrapper>
  );
};

const Wrapper: React.FC<PropsWithChildren> = ({ children }) => {
  return (
    <div className="flex min-h-[100vh] w-full flex-col items-center justify-center gap-2 px-6 dark:bg-volcanic-100 md:px-0">
      {children}
    </div>
  );
};

export default ShareConversationPage;
