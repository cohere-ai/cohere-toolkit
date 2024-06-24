import Cookies from 'js-cookie';

import { useAuthConfig } from '@/hooks/authConfig';

/**
 * Hook which redirects to the Google login/register page.
 * This hook is used on the auth host app's login page, in combination with `ssrUseLogin` called
 * in `getServerSideProps`.
 *
 * Upon successful login, the `useSession` hook will provide a valid session.
 */
export const useOidcAuthRoute = () => {
  const authConfig = useAuthConfig();

  if (!authConfig.loginStrategies) {
    throw new Error('ssrUseLogin() and useLogin() may only be used in an auth host app.');
  }

  const handleOidcAuth = {
    start({
      strategy,
      authorizationEndpoint,
      redirectToReadMe = false,
      redirect,
      freeCreditCode,
      inviteHash,
      recaptchaToken = '',
    }: {
      strategy: string;
      authorizationEndpoint: string;
      redirectToReadMe?: boolean;
      redirect?: string;
      freeCreditCode?: string;
      inviteHash?: string;
      recaptchaToken?: string;
    }) {
      if (!authConfig.loginStrategies) {
        throw new Error('ssrUseLogin() and useLogin() may only be used in an auth host app.');
      }

      const strategyConfig = authConfig.loginStrategies.find(
        (strategyConfig) => strategyConfig.strategy === strategy
      );

      if (!strategyConfig) {
        throw new Error(`Strategy ${strategy} not found in authConfig`);
      }

      const oauthState = {
        state: Math.random().toString(36).substring(7),
        ...(freeCreditCode && { freeCreditCode }),
        ...(inviteHash && { inviteHash }),
        ...(redirect && { redirect }),
        redirectToReadMe,
        recaptchaToken,
      };
      const state = JSON.stringify(oauthState);

      const url = `${authorizationEndpoint}?${new URLSearchParams({
        response_type: 'code',
        scope: 'openid email profile',
        redirect_uri: `${authConfig.baseUrl}/auth/${encodeURIComponent(
          strategyConfig.strategy.toLowerCase()
        )}`,
        prompt: 'select_account consent',
        state,
        ...(strategyConfig.client_id && { client_id: strategyConfig.client_id }),
      }).toString()}`;

      window.location.assign(url);
    },
  };

  return {
    oidcAuth: handleOidcAuth,
  };
};
