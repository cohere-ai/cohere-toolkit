import { UseMutateAsyncFunction, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';

import {
  ChatResponseEvent,
  Citation,
  CohereChatRequest,
  CohereNetworkError,
  Document,
  FinishReason,
  StreamCitationGeneration,
  StreamEnd,
  StreamEvent,
  StreamSearchResults,
  StreamStart,
  StreamTextGeneration,
  StreamToolInput,
  StreamToolResult,
  isCohereNetworkError,
  isSessionUnavailableError,
  isStreamError,
} from '@/cohere-client';
import { DEPLOYMENT_COHERE_PLATFORM, TOOL_PYTHON_INTERPRETER_ID } from '@/constants';
import { useRouteChange } from '@/hooks/route';
import { StreamingChatParams, useStreamChat } from '@/hooks/streamChat';
import { useCitationsStore, useConversationStore, useFilesStore, useParamsStore } from '@/stores';
import { OutputFiles } from '@/stores/slices/citationsSlice';
import {
  BotState,
  ChatMessage,
  ErrorMessage,
  MessageType,
  StreamingMessage,
  createAbortedMessage,
  createErrorMessage,
  createLoadingMessage,
} from '@/types/message';
import {
  createStartEndKey,
  fixMarkdownImagesInText,
  isAbortError,
  isGroundingOn,
  replaceTextWithCitations,
} from '@/utils';
import { parsePythonInterpreterToolFields } from '@/utils/tools';

const USER_ERROR_MESSAGE = 'Something went wrong. This has been reported. ';
const ABORT_REASON_USER = 'USER_ABORTED';

type IdToDocument = { [documentId: string]: Document };

type ChatRequestOverrides = Pick<
  CohereChatRequest,
  'temperature' | 'model' | 'preamble' | 'tools' | 'file_ids'
>;

export type HandleSendChat = (
  {
    currentMessages,
    suggestedMessage,
  }: {
    currentMessages?: ChatMessage[];
    suggestedMessage?: string;
  },
  overrides?: ChatRequestOverrides,
  regenerating?: boolean
) => Promise<void>;

export const useChat = (config?: { onSend?: (msg: string) => void }) => {
  const { chatMutation, abortController } = useStreamChat();
  const { mutateAsync: streamChat } = chatMutation;

  const {
    params: { temperature, tools, model, deployment },
  } = useParamsStore();
  const {
    conversation: { id, messages },
    setConversation,
    setPendingMessage,
  } = useConversationStore();
  const { addSearchResults, addCitation, saveOutputFiles } = useCitationsStore();
  const {
    files: { composerFiles },
    clearComposerFiles,
  } = useFilesStore();
  const queryClient = useQueryClient();
  const fileIds = composerFiles.map((file) => file.id);

  const [userMessage, setUserMessage] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState<StreamingMessage | null>(null);

  useRouteChange({
    onRouteChangeStart: () => {
      abortController.current?.abort();
      setStreamingMessage(null);
    },
  });

  const saveCitations = (
    generationId: string,
    citations: Citation[],
    documentsMap: {
      [documentId: string]: Document;
    }
  ) => {
    for (const citation of citations) {
      const startEndKey = createStartEndKey(citation.start ?? 0, citation.end ?? 0);
      const documents = (citation?.document_ids || [])
        .map((id) => documentsMap[id])
        // When we use documents for RAG, we don't get the documents split up by snippet
        // and their new ids until the final response. In the future, we will potentially
        // get the snippets in the citation-generation event and we can inject them here.
        .filter(Boolean);
      addCitation(generationId, startEndKey, documents);
    }
  };

  const mapDocuments = (documents: Document[]) => {
    return documents.reduce<{ documentsMap: IdToDocument; outputFilesMap: OutputFiles }>(
      ({ documentsMap, outputFilesMap }, doc) => {
        const docId = doc?.document_id ?? '';
        const toolName = (doc?.tool_name ?? '').toLowerCase();
        const newOutputFilesMapEntry: OutputFiles = {};

        if (toolName === TOOL_PYTHON_INTERPRETER_ID) {
          const { outputFile } = parsePythonInterpreterToolFields(doc);

          if (outputFile) {
            newOutputFilesMapEntry[outputFile.filename] = {
              name: outputFile.filename,
              data: outputFile.b64_data,
              documentId: docId,
            };
          }
        }
        return {
          documentsMap: { ...documentsMap, [docId]: doc },
          outputFilesMap: { ...outputFilesMap, ...newOutputFilesMapEntry },
        };
      },
      { documentsMap: {}, outputFilesMap: {} }
    );
  };

  const mapOutputFiles = (outputFiles: { output_file: string; text: string }[] | undefined) => {
    return outputFiles?.reduce<OutputFiles>((outputFilesMap, outputFile) => {
      try {
        const outputFileObj: { filename: string; b64_data: string } = JSON.parse(
          outputFile.output_file
        );
        return {
          ...outputFilesMap,
          [outputFileObj.filename]: {
            name: outputFileObj.filename,
            data: outputFileObj.b64_data,
          },
        };
      } catch (e) {
        console.error('Could not parse output_file', e);
      }
      return outputFilesMap;
    }, {});
  };

  const handleStreamConverse = async ({
    newMessages,
    request,
    headers,
    streamConverse,
  }: {
    newMessages: ChatMessage[];
    request: CohereChatRequest;
    headers: Record<string, string>;
    streamConverse: UseMutateAsyncFunction<
      StreamEnd | undefined,
      CohereNetworkError,
      StreamingChatParams,
      unknown
    >;
  }) => {
    setConversation({ messages: newMessages });
    const isRAGOn = isGroundingOn(request?.tools || [], request.file_ids || []);
    setStreamingMessage(
      createLoadingMessage({
        text: '',
        isRAGOn,
      })
    );

    let botResponse = '';
    let conversationId = '';
    let generationId = '';
    let citations: Citation[] = [];
    let documentsMap: IdToDocument = {};
    let outputFiles: OutputFiles = {};
    let toolEvents: StreamToolInput[] = [];

    try {
      clearComposerFiles();

      await streamConverse({
        request,
        headers,
        onRead: (eventData: ChatResponseEvent) => {
          switch (eventData.event) {
            case StreamEvent.STREAM_START: {
              const data = eventData.data as StreamStart;
              setIsStreaming(true);
              conversationId = data?.conversation_id ?? '';
              generationId = data?.generation_id ?? '';
              break;
            }

            case StreamEvent.TEXT_GENERATION: {
              const data = eventData.data as StreamTextGeneration;
              botResponse += data?.text ?? '';
              setStreamingMessage({
                type: MessageType.BOT,
                state: BotState.TYPING,
                text: botResponse,
                generationId,
                isRAGOn,
                originalText: botResponse,
                toolEvents,
              });
              break;
            }

            // This event only occurs when we use tools.
            case StreamEvent.SEARCH_RESULTS: {
              const data = eventData.data as StreamSearchResults;
              const documents = data?.documents ?? [];

              const { documentsMap: newDocumentsMap, outputFilesMap: newOutputFilesMap } =
                mapDocuments(documents);
              documentsMap = { ...documentsMap, ...newDocumentsMap };
              outputFiles = { ...outputFiles, ...newOutputFilesMap };
              break;
            }

            case StreamEvent.TOOL_INPUT: {
              const data = eventData.data as StreamToolInput;
              toolEvents.push(data);

              setStreamingMessage({
                type: MessageType.BOT,
                state: BotState.TYPING,
                text: botResponse,
                isRAGOn,
                generationId,
                originalText: botResponse,
                toolEvents,
              });
              break;
            }

            // This event only occurs when we're using experimental langchain multihop.
            case StreamEvent.TOOL_RESULT: {
              const data = eventData.data as StreamToolResult;
              if (data.tool_name.toLowerCase() === TOOL_PYTHON_INTERPRETER_ID) {
                const resultsWithOutputFile = data.result.filter((r: any) => r.output_file);
                outputFiles = { ...mapOutputFiles(resultsWithOutputFile) };
                saveOutputFiles(outputFiles);
              }

              setStreamingMessage({
                type: MessageType.BOT,
                state: BotState.TYPING,
                text: botResponse,
                isRAGOn,
                generationId,
                originalText: botResponse,
                toolEvents,
              });

              break;
            }

            case StreamEvent.CITATION_GENERATION: {
              const data = eventData.data as StreamCitationGeneration;
              const newCitations = [...(data?.citations ?? [])];
              newCitations.sort((a, b) => (a.start ?? 0) - (b.start ?? 0));
              citations.push(...newCitations);
              citations.sort((a, b) => (a.start ?? 0) - (b.start ?? 0));
              saveCitations(generationId, newCitations, documentsMap);

              setStreamingMessage({
                type: MessageType.BOT,
                state: BotState.TYPING,
                text: replaceTextWithCitations(botResponse, citations, generationId),
                citations,
                isRAGOn,
                generationId,
                originalText: botResponse,
                toolEvents,
              });
              break;
            }

            case StreamEvent.STREAM_END: {
              const data = eventData.data as StreamEnd;

              conversationId = data?.conversation_id ?? '';

              if (id !== conversationId) {
                setConversation({ id: conversationId });
              }
              // Make sure our URL is up to date with the conversationId
              if (!window.location.pathname.includes(`c/${conversationId}`) && conversationId) {
                window?.history?.replaceState('', '', `c/${conversationId}`);
                queryClient.invalidateQueries({ queryKey: ['conversations'] });
              }

              const responseText = data.text ?? '';

              addSearchResults(data?.search_results ?? []);

              // When we use documents for RAG, we don't get the documents split up by snippet
              // and their new ids until the final response. In the future, we will potentially
              // get the snippets in the citation-generation event and we can inject them there.
              const { documentsMap: newDocumentsMap, outputFilesMap: newOutputFilesMap } =
                mapDocuments(data.documents ?? []);
              documentsMap = { ...documentsMap, ...newDocumentsMap };
              outputFiles = { ...outputFiles, ...newOutputFilesMap };

              saveCitations(generationId, citations, documentsMap);

              const finalText = isRAGOn
                ? replaceTextWithCitations(
                    // TODO(@wujessica): temporarily use the text generated from the stream when MAX_TOKENS
                    // because the final response doesn't give us the full text yet. Note - this means that
                    // citations will only appear for the first 'block' of text generated.
                    data?.finish_reason === FinishReason.FINISH_REASON_MAX_TOKENS
                      ? botResponse
                      : responseText,
                    citations,
                    generationId
                  )
                : botResponse;

              setStreamingMessage({
                type: MessageType.BOT,
                state: BotState.FULFILLED,
                generationId,
                // TODO(@wujessica): TEMPORARY - we don't pass citations for langchain multihop right now
                // so we need to manually apply this fix. Otherwise, this comes for free when we call
                // `replaceTextWithCitations`.
                text: citations.length > 0 ? finalText : fixMarkdownImagesInText(finalText),
                citations,
                isRAGOn,
                originalText: isRAGOn ? responseText : botResponse,
                toolEvents,
              });

              break;
            }
          }
        },
        onHeaders: () => {},
        onFinish: () => {
          setIsStreaming(false);
          setConversation({ isSessionAvailable: true });
        },
        onError: (e) => {
          citations = [];
          if (isCohereNetworkError(e)) {
            const networkError = e;
            let errorMessage = USER_ERROR_MESSAGE;

            if (isSessionUnavailableError(e)) {
              setConversation({ isSessionAvailable: false });
            }

            setConversation({
              messages: newMessages.map((m, i) =>
                i < newMessages.length - 1
                  ? m
                  : { ...m, error: `[${networkError.status}] ${errorMessage}` }
              ),
            });
          } else if (isStreamError(e)) {
            const streamError = e;

            const lastMessage: ErrorMessage = createErrorMessage({
              text: botResponse,
              error: `[${streamError.code}] ${USER_ERROR_MESSAGE}`,
            });

            setConversation({ messages: [...newMessages, lastMessage] });
          } else {
            if (isAbortError(e)) {
              if (abortController.current?.signal.reason === ABORT_REASON_USER) {
                setConversation({
                  messages: [
                    ...newMessages,
                    createAbortedMessage({
                      text: botResponse,
                    }),
                  ],
                });
              }
            } else {
              let error =
                (e as CohereNetworkError)?.message ||
                'Unable to generate a response since an error was encountered.';

              if (error === 'network error' && deployment === DEPLOYMENT_COHERE_PLATFORM) {
                error += ' (Ensure a COHERE_API_KEY is configured in the .env file)';
              }
              setConversation({
                messages: [
                  ...newMessages,
                  createErrorMessage({
                    text: botResponse,
                    error,
                  }),
                ],
              });
            }
          }
          setIsStreaming(false);
          setStreamingMessage(null);
          setPendingMessage(null);
        },
      });
    } catch (e) {
      if (isCohereNetworkError(e) && e?.status) {
        let errorMessage = USER_ERROR_MESSAGE;

        if (isSessionUnavailableError(e)) {
          setConversation({ isSessionAvailable: false });
        }

        setConversation({
          messages: newMessages.map((m, i) =>
            i < newMessages.length - 1
              ? m
              : { ...m, error: `[${(e as CohereNetworkError)?.status}] ${errorMessage}` }
          ),
        });
      }

      setIsStreaming(false);
      setStreamingMessage(null);
      setPendingMessage(null);
    }
  };

  const getChatRequest = (message: string, overrides?: ChatRequestOverrides): CohereChatRequest => {
    const { tools: overrideTools, ...restOverrides } = overrides ?? {};
    return {
      message,
      conversation_id: id,
      tools: !!overrideTools?.length
        ? overrideTools
        : tools && tools.length > 0
        ? tools
        : undefined,
      file_ids: fileIds && fileIds.length > 0 ? fileIds : undefined,
      temperature,
      model,
      ...restOverrides,
    };
  };

  const handleChat: HandleSendChat = async (
    { currentMessages = messages, suggestedMessage },
    overrides?: ChatRequestOverrides
  ) => {
    const message = (suggestedMessage || userMessage || '').trim();
    if (message.length === 0 || isStreaming) {
      return;
    }

    config?.onSend?.(message);
    setUserMessage('');

    const request = getChatRequest(message, overrides);
    const headers = { 'Deployment-Name': deployment ?? '' };
    let newMessages: ChatMessage[] = currentMessages;

    if (streamingMessage) {
      newMessages.push(streamingMessage);
      setStreamingMessage(null);
    }
    newMessages = newMessages.concat({
      type: MessageType.USER,
      text: message,
      files: composerFiles,
    });

    await handleStreamConverse({ newMessages, request, headers, streamConverse: streamChat });
  };

  const handleRetry = () => {
    const latestMessage = messages[messages.length - 1];

    if (latestMessage.type === MessageType.USER) {
      // Remove last message (user message)
      const latestMessageRemoved = messages.slice(0, -1);
      const latestUserMessage = latestMessage.text;
      handleChat({ suggestedMessage: latestUserMessage, currentMessages: latestMessageRemoved });
    } else if (latestMessage.type === MessageType.BOT) {
      // Remove last messages (bot aborted message and user message)
      const latestMessagesRemoved = messages.slice(0, -2);
      const latestUserMessage = messages[messages.length - 2].text;
      handleChat({ suggestedMessage: latestUserMessage, currentMessages: latestMessagesRemoved });
    }
  };

  const handleStop = () => {
    abortController.current?.abort(ABORT_REASON_USER);
  };

  return {
    userMessage,
    isStreaming,
    handleSend: handleChat,
    handleStop,
    handleRetry,
    streamingMessage,
    setPendingMessage,
    setUserMessage,
  };
};
