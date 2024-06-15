import { useServerAuthStrategies } from '@/hooks/authStrategies';

export const useAuthConfig = (): {
  loginUrl: string;
  registerUrl: string;
  logoutUrl: string;
  login: { strategy: string; client_id: string; authorization_endpoint: string }[];
  baseUrl: string;
} => {
  const { data: authStrategies } = useServerAuthStrategies();

  return {
    loginUrl: '/login',
    registerUrl: '/register',
    logoutUrl: '/logout',
    login: authStrategies ? authStrategies : [],
    baseUrl: 'http://localhost:4000',
  };
};
