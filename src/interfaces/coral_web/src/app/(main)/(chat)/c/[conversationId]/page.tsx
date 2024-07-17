'use client';

import { NextPage } from 'next';
import { useContext, useEffect } from 'react';

import { Document } from '@/cohere-client';
import { ConnectDataModal } from '@/components/ConnectDataModal';
import Conversation from '@/components/Conversation';
import { ConversationError } from '@/components/ConversationError';
import { Spinner } from '@/components/Shared';
import { TOOL_PYTHON_INTERPRETER_ID } from '@/constants';
import { BannerContext } from '@/context/BannerContext';
import { ModalContext } from '@/context/ModalContext';
import { useChatRoutes } from '@/hooks/chatRoutes';
import { useConversation } from '@/hooks/conversation';
import { useListAllDeployments } from '@/hooks/deployments';
import { useExperimentalFeatures } from '@/hooks/experimentalFeatures';
import { useShowUnauthedToolsModal } from '@/hooks/tools';
import { useCitationsStore, useConversationStore, useParamsStore } from '@/stores';
import { OutputFiles } from '@/stores/slices/citationsSlice';
import { createStartEndKey, mapHistoryToMessages } from '@/utils';
import { parsePythonInterpreterToolFields } from '@/utils/tools';

const Page: NextPage = () => {
  const { conversationId } = useChatRoutes();
  const { setConversation } = useConversationStore();

  const { addCitation, saveOutputFiles } = useCitationsStore();
  const {
    params: { deployment },
    setParams,
  } = useParamsStore();
  const { show: showUnauthedToolsModal, onDismissed } = useShowUnauthedToolsModal();
  const { data: allDeployments } = useListAllDeployments();
  const { data: experimentalFeatures } = useExperimentalFeatures();
  const isLangchainModeOn = !!experimentalFeatures?.USE_EXPERIMENTAL_LANGCHAIN;

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

  return isLoading ? (
    <div className="flex h-full flex-grow flex-col items-center justify-center">
      <Spinner />
    </div>
  ) : isError ? (
    <ConversationError error={error} />
  ) : (
    <Conversation conversationId={conversationId} startOptionsEnabled />
  );
};

export default Page;
