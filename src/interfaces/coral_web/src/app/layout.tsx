import { Metadata } from 'next';

import { LayoutProviders } from '@/app/_providers';
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
  return (
    <html lang="en" className={cn({ dark: env.NEXT_PUBLIC_DARK_MODE })}>
      <body>
        <LayoutProviders>{children}</LayoutProviders>
      </body>
    </html>
  );
};

export default Layout;
