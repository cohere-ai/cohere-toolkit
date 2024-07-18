'use client';

import { NextPage } from 'next';
import { useParams, useRouter } from 'next/navigation';
import { useEffect } from 'react';

import { Text } from '@/components/Shared';
import { useAuthConfig } from '@/hooks/authConfig';
import { useSession } from '@/hooks/session';
import { getQueryString } from '@/utils';

/**
 * @description This page handles callbacks from OAuth providers and forwards the request to the backend.
 */
const CompleteOauthPage: NextPage = () => {
  const router = useRouter();
  const params = useParams();
  const { oidcSSOMutation, googleSSOMutation } = useSession();
  const redirect = getQueryString(params.redirect_uri);
  const { loginStrategies: ssoLogins } = useAuthConfig();

  const loginType = ssoLogins.find(
    (login) => encodeURIComponent(login.strategy.toLowerCase()) == params.strategy
  );

  useEffect(() => {
    if (!loginType) {
      return;
    }

    if (loginType.strategy.toLowerCase() === 'google') {
      googleSSOMutation.mutate(
        {
          code: params.code as string,
        },
        {
          onSuccess: () => {
            router.push(redirect || '/');
          },
          onError: () => {
            router.push('/login');
          },
        }
      );
      return;
    }

    oidcSSOMutation.mutate(
      {
        code: params.code as string,
        strategy: loginType.strategy,
      },
      {
        onSuccess: () => {
          router.push(redirect || '/');
        },
        onError: () => {
          router.push('/login');
        },
      }
    );
  }, [loginType]);

  return (
    <div className="flex flex-col items-center justify-center">
      <Text as="h1" styleAs="h3">
        Logging in
      </Text>
    </div>
  );
};

export default CompleteOauthPage;
