import { LayoutProviders } from '@/app/_providers';
import '@/styles/main.css';

const Layout: React.FC<React.PropsWithChildren> = ({ children }) => {
  return (
    <html lang="en">
      <body>
        <LayoutProviders>{children}</LayoutProviders>
      </body>
    </html>
  );
};

export default Layout;
