import { Metadata, NextPage } from 'next';

import Login from './Login';

export const metadata: Metadata = {
  title: 'Login',
};

const LoginPage: NextPage = () => {
  return <Login />;
};

export default LoginPage;
