import { useQuery } from '@tanstack/react-query';

import { useCohereClient } from '@/cohere-client';
import { ExperimentalFeatures } from '@/cohere-client/generated/types';

/**
 * @description Hook to get experimental features on/off status.
 */
export const useExperimentalFeatures = () => {
  const cohereClient = useCohereClient();

  return useQuery<ExperimentalFeatures>({
    queryKey: ['experimentalFeatures'],
    queryFn: async () => {
      try {
        return await cohereClient.getExperimentalFeatures();
      } catch (e) {
        console.error(e);
        throw e;
      }
    },
    refetchOnWindowFocus: false,
  });
};
