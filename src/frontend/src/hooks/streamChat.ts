import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useEffect, useRef } from 'react';

import {
  ChatResponseEvent as ChatResponse,
  CohereChatRequest,
  CohereFinishStreamError,
  CohereNetworkError,
  Conversation,
  FinishReason,
  StreamEnd,
  StreamEvent,
  isUnauthorizedError,
  useCohereClient,
} from '@/cohere-client';

interface StreamingParams {
  onRead: (data: ChatResponse) => void;
  onHeaders: (headers: Headers) => void;
  onFinish: () => void;
  onError: (error: unknown) => void;
}

export interface StreamingChatParams extends StreamingParams {
  request: CohereChatRequest;
  headers: Record<string, string>;
}

const getUpdatedConversations =
  (conversationId: string | undefined, description: string = '') =>
  (conversations: Conversation[] | undefined) => {
    return conversations?.map((c) => {
      if (c.id !== conversationId) return c;

      return {
        ...c,
        description,
        updatedAt: new Date().toISOString(),
      };
    });
  };

export const useStreamChat = () => {
  const abortControllerRef = useRef<AbortController | null>(null);
  const cohereClient = useCohereClient();
  const queryClient = useQueryClient();

  useEffect(() => {
    return () => {
      abortControllerRef.current?.abort();
    };
  }, []);

  const retry = (failCount: number, error: CohereNetworkError) => {
    // we allow 1 retry for 401 errors
    if (isUnauthorizedError(error)) {
      return failCount < 1;
    }
    return false;
  };

  const updateConversationHistory = (data?: StreamEnd) => {
    if (!data) return;

    queryClient.setQueryData<Conversation[]>(
      ['conversations'],
      getUpdatedConversations(data?.conversation_id ?? '', data?.text)
    );
  };

  const chatMutation = useMutation<StreamEnd | undefined, CohereNetworkError, StreamingChatParams>({
    mutationFn: async (params: StreamingChatParams) => {
      try {
        queryClient.setQueryData<Conversation[]>(
          ['conversations'],
          getUpdatedConversations(params.request.conversation_id ?? '', params.request.message)
        );

        abortControllerRef.current = new AbortController();

        const { request, headers, onRead, onError, onFinish } = params;
        await cohereClient.chat({
          request,
          headers,
          signal: abortControllerRef.current.signal,
          onMessage: (event) => {
            try {
              if (!event.data) return;
              const data = JSON.parse(event.data);
              if (data?.isFinished === true && data?.event === StreamEvent.STREAM_END) {
                const { chatStreamEndEvent: event } = data;
                if (event.finish_reason !== FinishReason.FINISH_REASON_COMPLETE) {
                  throw new CohereFinishStreamError(event?.finish_reason);
                }
              }
              onRead(data);
            } catch (e) {
              throw new Error('unable to parse event data');
            }
          },
          onError: (err) => {
            onError(err);
            // Rethrow to stop the operation
            throw err;
          },
          onClose: () => {
            onFinish();
          },
        });
      } catch (e) {
        if (isUnauthorizedError(e)) {
          await queryClient.invalidateQueries({ queryKey: ['defaultAPIKey'] });
        }
        return Promise.reject(e);
      }
    },
    retry,
    onSuccess: updateConversationHistory,
  });

  return {
    chatMutation,
    abortController: abortControllerRef,
  };
};
