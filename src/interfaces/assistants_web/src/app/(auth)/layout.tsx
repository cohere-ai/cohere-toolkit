import { WelcomePage } from '@/components/WelcomePage';

const AuthLayout: React.FC<React.PropsWithChildren> = ({ children }) => {
  return <WelcomePage>{children}</WelcomePage>;
};

export default AuthLayout;
