import { ListAuthStrategy } from '@/cohere-client';
import { env } from '@/env.mjs';
import { useServerAuthStrategies } from '@/hooks/authStrategies';

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
