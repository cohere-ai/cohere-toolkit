'use client';

import { Transition } from '@headlessui/react';
import { useEffect } from 'react';

import { Document, ManagedTool } from '@/cohere-client';
import AgentRightPanel from '@/components/Agents/AgentRightPanel';
import { ConnectDataModal } from '@/components/ConnectDataModal';
import Conversation from '@/components/Conversation';
import { ConversationError } from '@/components/ConversationError';
import { Spinner } from '@/components/Shared';
import { TOOL_PYTHON_INTERPRETER_ID } from '@/constants';
import { useContextStore } from '@/context';
import { useAgent } from '@/hooks/agents';
import { useIsDesktop } from '@/hooks/breakpoint';
import { useConversation } from '@/hooks/conversation';
import { useListTools, useShowUnauthedToolsModal } from '@/hooks/tools';
import { useAgentsStore, useCitationsStore, useConversationStore, useParamsStore } from '@/stores';
import { OutputFiles } from '@/stores/slices/citationsSlice';
import { cn, createStartEndKey, mapHistoryToMessages } from '@/utils';
import { parsePythonInterpreterToolFields } from '@/utils/tools';

const Chat: React.FC<{ agentId?: string; conversationId?: string }> = ({
  agentId,
  conversationId,
}) => {
  const { show: showUnauthedToolsModal, onDismissed } = useShowUnauthedToolsModal();
  const { data: agent } = useAgent({ agentId });
  const { data: tools } = useListTools();
  const { setConversation } = useConversationStore();
  const { addCitation, resetCitations, saveOutputFiles } = useCitationsStore();
  const { setParams, resetFileParams } = useParamsStore();
  const {
    agents: { isAgentsRightPanelOpen },
  } = useAgentsStore();
  const isDesktop = useIsDesktop();

  const { open, close } = useContextStore();

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

  // Reset citations and file params when switching between conversations
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
  }, [conversation?.id, conversation?.messages.length, setConversation]);

  const content = isLoading ? (
    <div className="flex h-full flex-grow flex-col items-center justify-center">
      <Spinner />
    </div>
  ) : isError ? (
    <ConversationError error={error} />
  ) : (
    <Conversation conversationId={conversationId} agent={agent} tools={tools} startOptionsEnabled />
  );

  return (
    <div className="flex w-full">
      <div className="flex-grow">{content}</div>
      <Transition
        show={isAgentsRightPanelOpen || isDesktop}
        as="div"
        className={cn('dark:bg-volcanic-100', {
          'mr-4 hidden w-[280px] flex-shrink-0 md:flex lg:w-[360px]': isDesktop,
          'absolute inset-0': isAgentsRightPanelOpen || !isDesktop,
        })}
        enter="transition-all transform ease-in-out duration-300"
        enterFrom="translate-x-full"
        enterTo="translate-x-0"
        leave="transition-all transform ease-in-out duration-300"
        leaveFrom="translate-x-0 opacity-100"
        leaveTo="translate-x-full opacity-0"
      >
        <AgentRightPanel />
      </Transition>
    </div>
  );
};

export default Chat;
