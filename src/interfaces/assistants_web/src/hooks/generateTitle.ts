import { useMutation, useQueryClient } from '@tanstack/react-query';

import { GenerateTitleResponse, useCohereClient } from '@/cohere-client';

export const useUpdateConversationTitle = () => {
  const cohereClient = useCohereClient();
  const queryClient = useQueryClient();
  return useMutation<GenerateTitleResponse, Error, string>({
    mutationFn: (conversationId) => cohereClient.generateTitle({ conversationId }),
    onSettled: () => queryClient.invalidateQueries({ queryKey: ['conversations'] }),
    retry: 1,
  });
};
