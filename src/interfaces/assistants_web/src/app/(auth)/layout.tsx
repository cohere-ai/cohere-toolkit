import { WelcomePage } from '@/components/Welcome/WelcomePage';

const AuthLayout: React.FC<React.PropsWithChildren> = ({ children }) => {
  return <WelcomePage>{children}</WelcomePage>;
};

export default AuthLayout;
