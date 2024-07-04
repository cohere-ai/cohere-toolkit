import { useQuery } from '@tanstack/react-query';

import { useCohereClient } from '@/cohere-client';

/**
 * @description Hook to get authentication methods supported by the server.
 */
export const useServerAuthStrategies = (options?: { enabled?: boolean }) => {
  const cohereClient = useCohereClient();
<<<<<<< HEAD
  return useQuery<{ strategy: string }[], Error>({
    queryKey: ['authStrategies'],
    queryFn: async () => {
      try {
        return await cohereClient.getAuthStrategies();
      } catch (e) {
        console.error(e);
        throw e;
      }
    },
=======
  return useQuery({
    queryKey: ['authStrategies'],
    queryFn: () => cohereClient.getAuthStrategies(),
>>>>>>> main
    refetchOnWindowFocus: false,
    ...options,
  });
};
