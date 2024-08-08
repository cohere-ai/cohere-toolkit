'use client';

import { useEffect } from 'react';

import { Document, ManagedTool } from '@/cohere-client';
import Conversation from '@/components/Conversation';
import { ConversationError } from '@/components/ConversationError';
import { TOOL_PYTHON_INTERPRETER_ID } from '@/constants';
import { useAgent } from '@/hooks/agents';
import { useConversation } from '@/hooks/conversation';
import { useListTools } from '@/hooks/tools';
import { useCitationsStore, useConversationStore, useParamsStore } from '@/stores';
import { OutputFiles } from '@/stores/slices/citationsSlice';
import { createStartEndKey, mapHistoryToMessages } from '@/utils';
import { parsePythonInterpreterToolFields } from '@/utils/tools';

const Chat: React.FC<{ agentId?: string; conversationId?: string }> = ({
  agentId,
  conversationId,
}) => {
  const { data: agent } = useAgent({ agentId });
  const { data: tools } = useListTools();
  const { setConversation } = useConversationStore();
  const { addCitation, resetCitations, saveOutputFiles } = useCitationsStore();
  const { setParams, resetFileParams } = useParamsStore();

  const {
    data: conversation,
    isError,
    error,
  } = useConversation({
    conversationId: conversationId,
  });

  // Reset citations and file params when switching between conversations
  useEffect(() => {
    resetFileParams();

    const agentTools =
      agent?.tools &&
      ((agent.tools
        .map((name) => (tools ?? [])?.find((t) => t.name === name))
        .filter((t) => t !== undefined) ?? []) as ManagedTool[]);

    const fileIds = conversation?.files.map((file) => file.id);

    setParams({
      tools: agentTools,
      fileIds,
    });

    if (conversationId) {
      setConversation({ id: conversationId });
    }
  }, [
    agent,
    conversation,
    tools,
    conversationId,
    setConversation,
    resetCitations,
    resetFileParams,
    setParams,
  ]);

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

  return isError ? (
    <ConversationError error={error} />
  ) : (
    <Conversation conversationId={conversationId} agent={agent} tools={tools} startOptionsEnabled />
  );
};

export default Chat;
