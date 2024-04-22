import { useQuery } from '@tanstack/react-query';

import { Deployment, useCohereClient } from '@/cohere-client';

/**
 * @description Hook to get available deployments.
 */
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

/**
 * @description Hook to get all possible deployments.
 */
export const useListAllDeployments = (options?: { enabled?: boolean }) => {
  const cohereClient = useCohereClient();
  return useQuery<Deployment[], Error>({
    queryKey: ['allDeployments'],
    queryFn: async () => {
      try {
        return await cohereClient.listAllDeployments();
      } catch (e) {
        console.error(e);
        throw e;
      }
    },
    refetchOnWindowFocus: false,
    ...options,
  });
};
