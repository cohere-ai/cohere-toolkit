import { useQuery } from '@tanstack/react-query';

import { ExperimentalFeatures, useCohereClient } from '@/cohere-client';

/**
 * @description Hook to get experimental features on/off status.
 */
export const useExperimentalFeatures = () => {
  const cohereClient = useCohereClient();

  return useQuery<ExperimentalFeatures>({
    queryKey: ['experimentalFeatures'],
    queryFn: async () => cohereClient.getExperimentalFeatures(),
    refetchOnWindowFocus: false,
  });
};
