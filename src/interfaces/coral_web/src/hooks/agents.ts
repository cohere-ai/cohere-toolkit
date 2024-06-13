import { useMutation } from '@tanstack/react-query';

import { CreateAgent, useCohereClient } from '@/cohere-client';

export const useCreateAgent = () => {
  const cohereClient = useCohereClient();
  return useMutation({
    mutationFn: async (request: CreateAgent) => {
      try {
        return await cohereClient.createAgent(request);
      } catch (e) {
        console.error(e);
        throw e;
      }
    },
  });
};
