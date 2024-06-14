import { useMemo } from 'react';
import { useServerAuthStrategies } from '@/hooks/authStrategies';

export const useAuthConfig = () => {
  const { data: authStrategies } = useServerAuthStrategies();

  const loginStrategies = useMemo(() => {
    return authStrategies ? authStrategies.filter((strategy) => strategy.strategy !== 'Basic') : [];
  }, [authStrategies]);

  return {
    loginUrl: '/login',
    registerUrl: '/register',
    logoutUrl: '/logout',
    login: loginStrategies,
    baseUrl: 'http://localhost:4000',
  };
};
