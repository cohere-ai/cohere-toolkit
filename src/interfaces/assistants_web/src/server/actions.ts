'use server';

import { cookies } from 'next/headers';

import { COOKIE_KEYS } from '@/constants';

export const clearAuthToken = async () => {
  const cookieStore = cookies();
  cookieStore.delete(COOKIE_KEYS.authToken);
};

export const setAuthToken = async (authToken: string) => {
  const cookieStore = cookies();
  cookieStore.set(COOKIE_KEYS.authToken, authToken);
};
