import Cookies from 'js-cookie';

/**
 * Hook which redirects to the Google login/register page.
 * This hook is used on the auth host app's login page, in combination with `ssrUseLogin` called
 * in `getServerSideProps`.
 *
 * Upon successful login, the `useSession` hook will provide a valid session.
 */
export const useGoogleAuthRoute = () => {
  // const authConfig = useAuthConfig();
  const authConfig = {
    login: {
      googleClientId: 'googleClientId',
    },
    baseUrl: 'baseUrl',
  };

  if (!authConfig.login) {
    throw new Error('ssrUseLogin() and useLogin() may only be used in an auth host app.');
  }

  const handleGoogleAuth = {
    start({
      redirectToReadMe = false,
      redirect,
      freeCreditCode,
      inviteHash,
      recaptchaToken = '',
    }: {
      redirectToReadMe?: boolean;
      redirect?: string;
      freeCreditCode?: string;
      inviteHash?: string;
      recaptchaToken?: string;
    }) {
      if (!authConfig.login) {
        throw new Error('ssrUseLogin() and useLogin() may only be used in an auth host app.');
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

      Cookies.set('google_oauth_state', state, {
        sameSite: 'lax',
        secure: true,
      });

      const url = `https://accounts.google.com/o/oauth2/v2/auth?${new URLSearchParams({
        response_type: 'code',
        client_id: authConfig.login.googleClientId,
        scope: 'openid email profile',
        redirect_uri: `${authConfig.baseUrl}/auth/complete`,
        prompt: 'select_account consent',
        state,
      }).toString()}`;

      window.location.assign(url);
    },
  };

  return {
    googleAuth: handleGoogleAuth,
  };
};
