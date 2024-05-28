import Cookies from 'js-cookie';

/**
 * Hook which redirects to the Github login/register page.
 * This hook is used on the auth host app's login page, in combination with `ssrUseLogin` called
 * in `getServerSideProps`.
 *
 * Upon successful login, the `useSession` hook will provide a valid session.
 */
export const useGithubAuthRoute = () => {
  const authConfig = useAuthConfig();

  if (!authConfig.login) {
    throw new Error('ssrUseLogin() and useLogin() may only be used in an auth host app.');
  }

  const handleGithubAuth = {
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

      Cookies.set('github_oauth_state', state, {
        sameSite: 'lax',
        secure: true,
      });

      const url = `https://github.com/login/oauth/authorize?${new URLSearchParams({
        client_id: authConfig.login.githubClientId,
        scope: 'user:email',
        state,
      }).toString()}`;

      window.location.assign(url);
    },
  };

  return {
    githubAuth: handleGithubAuth,
  };
};
