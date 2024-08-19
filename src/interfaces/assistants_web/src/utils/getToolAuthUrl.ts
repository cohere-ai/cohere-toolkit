/**
 * The Tool Auth URL is the URL that the Assistant will use to authenticate with the Tool.
 * It accepts configuring the frontend redirect URL by adding the `frontend_redirect_url` query parameter to the state.
 */
export const getToolAuthUrl = (toolAuthUrl?: string | null, customRedirect?: string) => {
  let authUrl;
  if (toolAuthUrl) {
    authUrl = new URL(toolAuthUrl);
    const state = authUrl.searchParams.get('state');

    if (state) {
      try {
        const stateJson = JSON.parse(state);
        stateJson.frontend_redirect = customRedirect ?? window.location.href;
        authUrl.searchParams.set('state', JSON.stringify(stateJson));
        return authUrl.href;
      } catch {
        // fail silently
      }
    }
  }
};
