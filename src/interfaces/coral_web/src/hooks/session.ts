// import { EventSourceMessage } from '@microsoft/fetch-event-source';
import { useLocalStorageValue } from '@react-hookz/web';
import { useMutation } from '@tanstack/react-query';
import { jwtDecode } from 'jwt-decode';
// import { useEffect, useRef } from 'react';
import { LOCAL_STORAGE_KEYS } from '@/constants';
import { useServerAuthStrategies } from '@/hooks/authStrategies';

import {
  useCohereClient,
} from '@/cohere-client';
import { on } from 'events';
import { useMemo } from 'react';
// import { useExperimentalFeatures } from '@/hooks/experimentalFeatures';

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
  const { data: authStrategies } = useServerAuthStrategies();
  const { value: authToken, set: setAuthToken } = useLocalStorageValue<string | undefined>(
    LOCAL_STORAGE_KEYS.authToken,
    {
      defaultValue: undefined,
    }
  );

  const isLoggedIn = useMemo(() => (
    (authStrategies && authStrategies.length > 0 && !!authToken) || !authStrategies || authStrategies.length === 0
  ), [authToken, authStrategies]);
  const cohereClient = useCohereClient();
  const session: UserSession = authToken ? jwtDecode(authToken).context : {};

  const loginMutation = useMutation({
    mutationFn: async (params: LoginParams) => {
      return cohereClient.login(params);
    },
    onSuccess: (data: { token: string }) => {
      setAuthToken(data.token);
      return new Promise((resolve) => resolve(data.token));
    }
  });

  const logoutMutation = useMutation({
    mutationFn: async () => {
      setAuthToken(undefined);
      return cohereClient.logout();
    },
  });

  const registerMutation = useMutation({
    mutationFn: async (params: RegisterParams) => {
      return cohereClient.createUser(params);
    },
  });

  return {
    session,
    authToken,
    isLoggedIn,
    loginMutation,
    logoutMutation,
    registerMutation,
  };
};
