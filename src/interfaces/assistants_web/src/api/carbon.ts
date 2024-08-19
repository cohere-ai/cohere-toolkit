export const createTokenFetcher =
  (userId: string) => async (): Promise<{ access_token: string; refresh_token: string }> => {
    const res = await fetch('/api/auth/carbon', { headers: { 'customer-id': userId } });

    return await res.json();
  };
