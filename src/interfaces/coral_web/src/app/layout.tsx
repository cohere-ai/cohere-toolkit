import { ClerkProvider } from '@clerk/nextjs';
import { Metadata } from 'next';
import { CookiesProvider } from 'next-client-cookies/server';
import { Html } from 'next/document';
import { cookies } from 'next/headers';

import { LayoutProviders } from '@/app/_providers';
import { COOKIE_KEYS } from '@/constants';
import { env } from '@/env.mjs';
import '@/styles/main.css';
import { cn } from '@/utils';

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
    // <html lang="en" className={cn({ dark: env.NEXT_PUBLIC_DARK_MODE })}>
    //   <body>
    //     <CookiesProvider>
    //       <LayoutProviders authToken={authToken}>{children}</LayoutProviders>
    //     </CookiesProvider>
    //   </body>
    // </html>
    <ClerkProvider>
      <html lang="en">
        <body>
          <LayoutProviders authToken={authToken}>{children}</LayoutProviders>
        </body>
      </html>
    </ClerkProvider>
  );
};

export default Layout;
