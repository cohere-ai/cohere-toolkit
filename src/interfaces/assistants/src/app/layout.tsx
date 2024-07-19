import { Metadata } from 'next';

import { LayoutProviders } from '@/app/_providers';
import '@/styles/main.css';

export const metadata: Metadata = {
  title: {
    template: '%s | Cohere',
    default: 'Chat | Cohere',
  },
};

const Layout: React.FC<React.PropsWithChildren> = ({ children }) => {
  return (
    <html lang="en" className="dark">
      <body>
        <LayoutProviders>{children}</LayoutProviders>
      </body>
    </html>
  );
};

export default Layout;
