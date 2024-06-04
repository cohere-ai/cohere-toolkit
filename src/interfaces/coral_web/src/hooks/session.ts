// import { EventSourceMessage } from '@microsoft/fetch-event-source';
import { useLocalStorageValue } from '@react-hookz/web';
import { useMutation } from '@tanstack/react-query';
// import { useEffect, useRef } from 'react';
import { LOCAL_STORAGE_KEYS } from '@/constants';

import {
  useCohereClient,
} from '@/cohere-client';
import { on } from 'events';
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
  user?: {
    email: string;
    name: string;
    avatarUrl: string;
    hasGoogleAuth: boolean;
    hasGithubAuth: boolean;
    hasEmailAuth: boolean;
  };
}

export const useSession = () => {
  const { value: authToken, set: setAuthToken } = useLocalStorageValue(
    LOCAL_STORAGE_KEYS.authToken,
    {
      defaultValue: undefined,
      initializeWithValue: false,
    }
  );

  const cohereClient = useCohereClient();
  const session: UserSession = {};

  const loginMutation = useMutation({
    mutationFn: async (params: LoginParams) => {
      return cohereClient.login(params);
    },
    onSuccess: (data) => {
      setAuthToken(data.token);
    }
  });

  const logoutMutation = useMutation({
    mutationFn: async () => {
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
    loginMutation,
    logoutMutation,
    registerMutation,
  };
};
