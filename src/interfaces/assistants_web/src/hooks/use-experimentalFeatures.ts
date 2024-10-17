import { useQuery } from '@tanstack/react-query';

import { useCohereClient } from '@/cohere-client';

export const useExperimentalFeatures = () => {
  const cohereClient = useCohereClient();
  return useQuery({
    queryKey: ['experimentalFeatures'],
    queryFn: () => cohereClient.getExperimentalFeatures(),
    refetchOnWindowFocus: false,
  });
};
