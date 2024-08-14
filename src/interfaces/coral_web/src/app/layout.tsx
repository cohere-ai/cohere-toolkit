import { Metadata } from 'next';
import { CookiesProvider } from 'next-client-cookies/server';
import { PublicEnvScript } from 'next-runtime-env';
import { cookies } from 'next/headers';

import { LayoutProviders } from '@/app/_providers';
import { COOKIE_KEYS } from '@/constants';
import '@/styles/main.css';

export const metadata: Metadata = {
  title: {
    template: '%s | Cohere',
    default: 'Chat | Cohere',
  },
};

const Layout: React.FC<React.PropsWithChildren> = ({ children }) => {
  const cookieStore = cookies();
  const authToken = cookieStore.get(COOKIE_KEYS.authToken)?.value;
  return (
    <html lang="en">
      <PublicEnvScript />
      <body>
        <CookiesProvider>
          <LayoutProviders authToken={authToken}>{children}</LayoutProviders>
        </CookiesProvider>
      </body>
    </html>
  );
};

export default Layout;
