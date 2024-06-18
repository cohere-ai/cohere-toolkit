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
  // const googleStrategy: { strategy: string, clientId: string } = authConfig.login.find((strategy) => strategy.strategy === 'Google') || {
  //   strategy: "Google",
  //   clientId: "fakeClientId"
  // };

  if (!authConfig.login) {
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
      if (!authConfig.login) {
        throw new Error('ssrUseLogin() and useLogin() may only be used in an auth host app.');
      }

      const strategyConfig = authConfig.login.find(
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
        client_id: strategyConfig.client_id,
        scope: 'openid email profile',
        redirect_uri: `${authConfig.baseUrl}/auth/${encodeURIComponent(
          strategyConfig.strategy.toLowerCase()
        )}`,
        prompt: 'select_account consent',
        state,
      }).toString()}`;

      window.location.assign(url);
    },
  };

  return {
    oidcAuth: handleOidcAuth,
  };
};
