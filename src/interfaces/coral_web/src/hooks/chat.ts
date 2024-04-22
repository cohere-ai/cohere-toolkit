import { UseMutateAsyncFunction, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/router';
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
  StreamQueryGeneration,
  StreamSearchResults,
  StreamStart,
  StreamTextGeneration,
  isCohereNetworkError,
  isSessionUnavailableError,
  isStreamError,
} from '@/cohere-client';
import { DEPLOYMENT_COHERE_PLATFORM } from '@/constants';
import { useRouteChange } from '@/hooks/route';
import { StreamingChatParams, useStreamChat } from '@/hooks/streamChat';
import { useCitationsStore, useConversationStore, useFilesStore, useParamsStore } from '@/stores';
import {
  BotState,
  ChatMessage,
  ErrorMessage,
  MessageType,
  StreamingMessage,
  createAbortedMessage,
  createErrorMessage,
  createLoadingMessage,
  isNotificationMessage,
} from '@/types/message';
import { createStartEndKey, isAbortError, isGroundingOn, replaceTextWithCitations } from '@/utils';

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
  const router = useRouter();

  const {
    params: { temperature, tools, model, deployment },
  } = useParamsStore();
  const {
    conversation: { id, messages },
    setConversation,
    setPendingMessage,
  } = useConversationStore();
  const { addSearchResults, addCitation } = useCitationsStore();
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
    let traceId = '';

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
              });
              break;
            }

            case StreamEvent.SEARCH_QUERIES_GENERATION: {
              const data = eventData.data as StreamQueryGeneration;
              const joinedQuery = data?.query;
              const searchQuery = !joinedQuery ? 'Deep diving' : `Searching: ${joinedQuery}`;
              setStreamingMessage(
                createLoadingMessage({
                  text: 'Deep diving',
                  isRAGOn,
                })
              );
              break;
            }

            // This event only occurs when we use tools.
            case StreamEvent.SEARCH_RESULTS: {
              const data = eventData.data as StreamSearchResults;
              const documents = data?.documents ?? [];

              documentsMap = documents.reduce<IdToDocument>(
                (idToDoc, doc) => ({ ...idToDoc, [doc.document_id ?? '']: doc }),
                {}
              );
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
              documentsMap = {
                ...documentsMap,
                ...(data?.documents ?? []).reduce<IdToDocument>(
                  (idToDoc, doc) => ({ ...idToDoc, [doc?.document_id ?? '']: doc }),
                  {}
                ),
              };

              saveCitations(generationId, citations, documentsMap);

              setStreamingMessage({
                type: MessageType.BOT,
                state: BotState.FULFILLED,
                generationId,
                text: isRAGOn
                  ? replaceTextWithCitations(
                      // TODO(jessica): temporarily use the text generated from the stream when MAX_TOKENS
                      // because the final response doesn't give us the full text yet. Note - this means that
                      // citations will only appear for the first 'block' of text generated.
                      // Fixes https://linear.app/cohereai/issue/CNV-1187
                      // Pending https://linear.app/cohereai/issue/CNV-1499
                      data?.finish_reason === FinishReason.FINISH_REASON_MAX_TOKENS
                        ? botResponse
                        : responseText,
                      citations,
                      generationId
                    )
                  : botResponse,
                citations,
                isRAGOn,
                originalText: isRAGOn ? responseText : botResponse,
                traceId,
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
    const latestMessage = newMessages[newMessages.length - 1];
    let notificationMessage = null;

    if (latestMessage && isNotificationMessage(latestMessage) && latestMessage.show) {
      notificationMessage = newMessages.pop();
    }
    if (streamingMessage) {
      newMessages.push(streamingMessage);
      setStreamingMessage(null);

      // The grounding notification message should always appear after the streamed bot message
      // when it they are being added to the chat history.
      if (notificationMessage) {
        newMessages.push(notificationMessage);
      }
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
