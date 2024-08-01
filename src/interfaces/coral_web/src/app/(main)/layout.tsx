import { NextPage } from 'next';
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

import { MainLayout } from '@/app/(main)/MainLayout';
import { COOKIE_KEYS } from '@/constants';

const Layout: NextPage<React.PropsWithChildren> = async ({ children }) => {
  const cookieStore = cookies();
  const authToken = cookieStore.get(COOKIE_KEYS.authToken);
  if (!authToken) {
    return redirect('/login');
  }
  return <MainLayout>{children}</MainLayout>;
};

export default Layout;
