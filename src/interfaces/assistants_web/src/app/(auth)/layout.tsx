import { WelcomePage } from '@/components/Auth';

const AuthLayout: React.FC<React.PropsWithChildren> = ({ children }) => {
  return <WelcomePage>{children}</WelcomePage>;
};

export default AuthLayout;
