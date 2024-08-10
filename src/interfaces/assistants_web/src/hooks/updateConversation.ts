import { useMutation, useQueryClient } from '@tanstack/react-query';

import { useCohereClient } from '@/cohere-client';
import { FulfilledMessage } from '@/types/message';

export const useUpdateMessage = () => {
  const cohereClient = useCohereClient();
  const queryClient = useQueryClient();
  return useMutation<{ conversationId: string }, Error, { conversationId: string, message: FulfilledMessage }>({
    mutationFn: async (payload) => {
      const { conversationId } = await cohereClient.updateMessage(payload.conversationId, payload.message)
      // await cohereClient.chat({ request: { conversation_id: conversationId } })
      return { conversationId }
    },
    onSettled: (payload) => queryClient.invalidateQueries({ queryKey: ['conversation', payload?.conversationId] }),
    retry: 1,
  });
};
