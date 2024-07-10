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
    async start({
      strategy,
      authorizationEndpoint,
      pkceEnabled,
      redirectToReadMe = false,
      redirect,
      freeCreditCode,
      inviteHash,
      recaptchaToken = '',
    }: {
      strategy: string;
      authorizationEndpoint: string;
      pkceEnabled: boolean;
      redirectToReadMe?: boolean;
      redirect?: string;
      freeCreditCode?: string;
      inviteHash?: string;
      recaptchaToken?: string;
    }) {
      if (!authConfig.loginStrategies) {
        throw new Error('ssrUseLogin() and useLogin() may only be used in an auth host app.');
      }

      let codeVerifier = '';
      let codeChallenge = '';
      if (pkceEnabled) {
        codeVerifier = generateCodeVerifier();
        codeChallenge = await generateCodeChallenge(codeVerifier);
        // TODO(AW): Should we put this in local storage instead?
        Cookies.set('code_verifier', codeVerifier, { sameSite: 'strict' });
        Cookies.set('code_challenge', codeChallenge, { sameSite: 'strict' });
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
        ...(pkceEnabled && { code_challenge: codeChallenge, code_challenge_method: 'S256' }),
      }).toString()}`;

      window.location.assign(url);
    },
  };

  return {
    oidcAuth: handleOidcAuth,
  };
};

function generateCodeVerifier(length: number = 128): string {
  const possibleCharacters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~';
  let codeVerifier = '';
  for (let i = 0; i < length; i++) {
    const randomIndex = Math.floor(Math.random() * possibleCharacters.length);
    codeVerifier += possibleCharacters.charAt(randomIndex);
  }
  return codeVerifier;
}

async function generateCodeChallenge(codeVerifier: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(codeVerifier);
  const digest = await crypto.subtle.digest('SHA-256', data);
  const base64Url = base64UrlEncode(digest);
  return base64Url;
}

function base64UrlEncode(buffer: ArrayBuffer): string {
  let base64 = '';
  const bytes = new Uint8Array(buffer);
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    base64 += String.fromCharCode(bytes[i]);
  }
  return btoa(base64).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}
