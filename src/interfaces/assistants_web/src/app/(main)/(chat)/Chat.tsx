'use client';

import { useEffect } from 'react';

import { Document, ToolDefinition } from '@/cohere-client';
import { Conversation, ConversationError } from '@/components/Conversation';
import { TOOL_PYTHON_INTERPRETER_ID } from '@/constants';
import { useAgent, useAvailableTools, useConversation, useListTools } from '@/hooks';
import { useCitationsStore, useConversationStore, useParamsStore } from '@/stores';
import { OutputFiles } from '@/stores/slices/citationsSlice';
import {
  createStartEndKey,
  fixInlineCitationsForMarkdown,
  mapHistoryToMessages,
  parsePythonInterpreterToolFields,
} from '@/utils';

const Chat: React.FC<{ agentId?: string; conversationId?: string }> = ({
  agentId,
  conversationId,
}) => {
  const { data: agent } = useAgent({ agentId });
  const { data: tools } = useListTools();
  const { setConversation } = useConversationStore();
  const { addCitation, saveOutputFiles } = useCitationsStore();
  const { setParams, resetFileParams } = useParamsStore();
  const { availableTools } = useAvailableTools({ agent, allTools: tools });

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
      (agent.tools
        .map((name) => (tools ?? [])?.find((t) => t.name === name))
        .filter(
          (t) => t !== undefined && availableTools.some((at) => at.name === t?.name)
        ) as ToolDefinition[]);

    const fileIds = conversation?.files.map((file) => file.id);

    setParams({
      temperature: agent?.temperature,
      tools: agentTools,
      fileIds,
    });

    if (conversationId) {
      setConversation({ id: conversationId });
    }
  }, [
    agent,
    tools,
    conversation,
    availableTools,
    setParams,
    resetFileParams,
    setConversation,
    conversationId,
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
      fixInlineCitationsForMarkdown(message.citations, message.text)?.forEach((citation) => {
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
    <Conversation agent={agent} tools={tools} startOptionsEnabled />
  );
};

export default Chat;
