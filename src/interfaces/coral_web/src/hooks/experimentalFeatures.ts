import { useQuery } from '@tanstack/react-query';

import { ExperimentalFeatures, useCohereClient } from '@/cohere-client';

export const useExperimentalFeatures = () => {
  const cohereClient = useCohereClient();

  return useQuery<ExperimentalFeatures>({
    queryKey: ['experimentalFeatures'],
    queryFn: async () => {
      try {
        return await cohereClient.listExperimentalFeatures();
      } catch (e) {
        console.error(e);
        throw e;
      }
    },
    refetchOnWindowFocus: false,
  });
};
