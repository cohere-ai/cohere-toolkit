export const createTokenFetcher =
  (userId: string) => async (): Promise<{ access_token: string }> => {
    const res = await fetch('/api/auth/carbon', { headers: { 'customer-id': userId } });

    const json = await res.json();

    return json.data;
  };
