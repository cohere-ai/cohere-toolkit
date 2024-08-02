import { useQuery } from '@tanstack/react-query';

import { ListAuthStrategy, useCohereClient } from '@/cohere-client';
import { NoNullProperties } from '@/types/util';

/**
 * @description Hook to get authentication methods supported by the server.
 */
export const useServerAuthStrategies = (options?: { enabled?: boolean }) => {
  const cohereClient = useCohereClient();
  return useQuery({
    queryKey: ['authStrategies'],
    queryFn: () => cohereClient.getAuthStrategies(),
    refetchOnWindowFocus: false,
    ...options,
  });
};

export const useAuthStrategies = () => {
  const cohereClient = useCohereClient();
  const queryInfo = useQuery({
    queryKey: ['authStrategies'],
    queryFn: () => cohereClient.getAuthStrategies(),
    refetchOnWindowFocus: false,
    refetchInterval: false,
  });

  return {
    ...queryInfo,
    data: {
      hasBasicAuth: queryInfo.data?.some((strategy) => strategy.strategy.toLowerCase() === 'basic'),
      ssoStrategies: (queryInfo.data?.filter(
        (strategy) =>
          strategy.strategy !== 'Basic' &&
          strategy.client_id !== null &&
          strategy.authorization_endpoint !== null
      ) ?? []) as NoNullProperties<ListAuthStrategy>[],
    },
  };
};
