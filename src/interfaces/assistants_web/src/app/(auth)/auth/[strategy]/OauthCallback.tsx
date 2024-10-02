'use client';

import { useParams, useRouter, useSearchParams } from 'next/navigation';
import { useEffect } from 'react';

import { Text } from '@/components/UI';
import { useAuthConfig, useNotify, useSession } from '@/hooks';
import { getQueryString } from '@/utils';

/**
 * @description This page handles callbacks from OAuth providers and forwards the request to the backend.
 */
const OauthCallback: React.FC = () => {
  const router = useRouter();
  const params = useParams();
  const search = useSearchParams();

  const { oidcSSOMutation, googleSSOMutation } = useSession();
  const redirect = getQueryString(search.get('redirect_uri'));
  const code = getQueryString(search.get('code'));
  const { loginStrategies: ssoLogins } = useAuthConfig();
  const notify = useNotify();

  const loginType = ssoLogins.find(
    (login) => encodeURIComponent(login.strategy.toLowerCase()) == params.strategy
  );

  useEffect(() => {
    if (!loginType || !code) {
      return;
    }

    if (loginType.strategy.toLowerCase() === 'google') {
      googleSSOMutation.mutate(
        {
          code,
        },
        {
          onSuccess: () => {
            router.push(redirect || '/');
          },
          onError: () => {
            notify.error('Failed to validate Google OAuth credentials');
            router.push('/login');
          },
        }
      );
      return;
    }

    oidcSSOMutation.mutate(
      {
        code,
        strategy: loginType.strategy,
      },
      {
        onSuccess: () => {
          router.push(redirect || '/');
        },
        onError: () => {
          notify.error('Failed to validate OAuth credentials');
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

export default OauthCallback;
