import { Metadata } from 'next';

import Logout from './Logout';

export const metadata: Metadata = {
  title: 'Logout',
};

const LogoutPage = () => {
  return <Logout />;
};

export default LogoutPage;
