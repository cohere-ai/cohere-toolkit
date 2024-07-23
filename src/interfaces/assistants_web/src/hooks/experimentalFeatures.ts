import { useQuery } from '@tanstack/react-query';

import { useCohereClient } from '@/cohere-client';

/**
 * @description Hook to get experimental features on/off status.
 */
export const useExperimentalFeatures = () => {
  const cohereClient = useCohereClient();

  return useQuery({
    queryKey: ['experimentalFeatures'],
    queryFn: () => cohereClient.getExperimentalFeatures(),
    refetchOnWindowFocus: false,
  });
};
