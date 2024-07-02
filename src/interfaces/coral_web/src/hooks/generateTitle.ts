import { useMutation, useQueryClient } from '@tanstack/react-query';

import { useCohereClient } from '@/cohere-client';

export const useUpdateConversationTitle = () => {
  const cohereClient = useCohereClient();
  const queryClient = useQueryClient();
  return useMutation<string | void, Error, string>({
    mutationFn: async (conversationId) => {
      try {
        const response = await cohereClient.generateTitle({ conversationId });
        return response.title;
      } catch (e) {
        if (e instanceof Error) {
          console.warn(e.message);
        }
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
    },
    retry: 1,
  });
};
