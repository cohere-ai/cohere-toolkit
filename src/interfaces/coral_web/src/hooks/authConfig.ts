import { ListAuthStrategy } from '@/cohere-client';
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
    baseUrl: window.location.href,
  };
};
