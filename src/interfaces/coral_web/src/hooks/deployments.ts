import { useQuery } from '@tanstack/react-query';

import { Deployment, useCohereClient } from '@/cohere-client';

export const useListDeployments = (options?: { enabled?: boolean }) => {
  const cohereClient = useCohereClient();
  return useQuery<Deployment[], Error>({
    queryKey: ['deployments'],
    queryFn: async () => {
      try {
        return await cohereClient.listDeployments();
      } catch (e) {
        console.error(e);
        throw e;
      }
    },
    refetchOnWindowFocus: false,
    ...options,
  });
};
