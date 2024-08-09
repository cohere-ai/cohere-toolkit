import { Metadata, NextPage } from 'next';

import SignInPage from '../sign-in/[[...sign-in]]/page';
import Login from './Login';

export const metadata: Metadata = {
  title: 'Login',
};

const LoginPage: NextPage = () => {
  return <SignInPage />;
};

export default LoginPage;
