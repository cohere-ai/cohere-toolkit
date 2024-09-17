import { useQuery } from '@tanstack/react-query';

import { ListAuthStrategy, useCohereClient } from '@/cohere-client';
import { env } from '@/env.mjs';

export const useAuthConfig = (): {
  loginUrl: string;
  registerUrl: string;
  logoutUrl: string;
  loginStrategies: ListAuthStrategy[];
  baseUrl: string;
} => {
  const { data: authStrategies = [] } = useServerAuthStrategies();

  return {
    loginUrl: '/login',
    registerUrl: '/register',
    logoutUrl: '/logout',
    loginStrategies: authStrategies,
    baseUrl: env.NEXT_PUBLIC_FRONTEND_HOSTNAME,
  };
};

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
