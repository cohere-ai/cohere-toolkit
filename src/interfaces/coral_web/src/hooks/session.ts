import { useLocalStorageValue } from '@react-hookz/web';
import { useMutation } from '@tanstack/react-query';
import Cookies from 'js-cookie';
import { jwtDecode } from 'jwt-decode';
import { useRouter } from 'next/navigation';
import { useCallback, useMemo } from 'react';

import { ApiError, JWTResponse, useCohereClient } from '@/cohere-client';
import { LOCAL_STORAGE_KEYS } from '@/constants';
import { useServerAuthStrategies } from '@/hooks/authStrategies';

interface LoginParams {
  email: string;
  password: string;
}

interface RegisterParams {
  name: string;
  email: string;
  password: string;
}

interface UserSession {
  email: string;
  fullname: string;
  id: string;
}

export const useSession = () => {
  const router = useRouter();
  const { data: authStrategies, isLoading: isLoadingStrategies } = useServerAuthStrategies();
  const {
    value: authToken,
    set: setAuthToken,
    remove: clearAuthToken,
  } = useLocalStorageValue<string | undefined>(LOCAL_STORAGE_KEYS.authToken, {
    defaultValue: undefined,
  });

  const isLoading = isLoadingStrategies || authToken === null;

  const isLoggedIn = useMemo(
    () =>
      (authStrategies && authStrategies.length > 0 && !!authToken) ||
      !authStrategies ||
      authStrategies.length === 0,
    [authToken, authStrategies]
  );

  const cohereClient = useCohereClient();
  const session = useMemo(
    () => (authToken ? (jwtDecode(authToken) as { context: UserSession }).context : null),
    [authToken]
  );

  const loginMutation = useMutation<JWTResponse | null, ApiError, LoginParams>({
    mutationFn: (params) => cohereClient.login(params),
    onSuccess: (data: JWTResponse | null) => {
      setAuthToken(data?.token);
      return new Promise((resolve) => resolve(data?.token));
    },
  });

  const logoutMutation = useMutation({
    mutationFn: () => {
      clearAuthToken();
      return cohereClient.logout();
    },
  });

  const registerMutation = useMutation({
    mutationFn: async (params: RegisterParams) => {
      return cohereClient.createUser({
        fullname: params.name,
        email: params.email,
        password: params.password,
      });
    },
  });

  const redirectToLogin = useCallback(() => {
    router.push(`/login?redirect_uri=${encodeURIComponent(window.location.href)}`);
  }, [router]);

  const googleSSOMutation = useMutation({
    mutationFn: async (params: { code: string }) => {
      return cohereClient.googleSSOAuth(params);
    },
    onSuccess: (data: { token: string }) => {
      setAuthToken(data.token);
      return new Promise((resolve) => resolve(data.token));
    },
  });

  const oidcSSOMutation = useMutation({
    mutationFn: async (params: { code: string; strategy: string }) => {
      const codeVerifier = Cookies.get('code_verifier');
      return cohereClient.oidcSSOAuth({
        ...params,
        ...(codeVerifier && { codeVerifier }),
      });
    },
    onSuccess: (data: { token: string }) => {
      setAuthToken(data.token);
      return new Promise((resolve) => resolve(data.token));
    },
    onSettled: () => {
      Cookies.remove('code_verifier');
      Cookies.remove('code_challenge');
    },
  });

  return {
    session,
    userId: session && 'id' in session ? session.id : 'user-id',
    authToken,
    isLoading,
    isLoggedIn,
    loginMutation,
    logoutMutation,
    registerMutation,
    redirectToLogin,
    googleSSOMutation,
    oidcSSOMutation,
  };
};
