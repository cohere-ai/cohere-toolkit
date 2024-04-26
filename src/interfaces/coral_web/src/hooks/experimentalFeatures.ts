import { useQuery } from '@tanstack/react-query';

import { useCohereClient } from '@/cohere-client';

export const useExperimentalFeatures = () => {
  const cohereClient = useCohereClient();

  return useQuery<boolean>({
    queryKey: ['experimentalFeatures'],
    queryFn: async () => {
      try {
        const data = await cohereClient.listExperimentalFeatures();
        return data.USE_EXPERIMENTAL_LANGCHAIN;
      } catch (e) {
        console.error(e);
        throw e;
      }
    },
    refetchOnWindowFocus: false,
  });
};
