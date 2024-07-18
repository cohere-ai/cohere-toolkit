import { Metadata } from 'next';

import Register from './Register';

export const metadata: Metadata = {
  title: 'Register',
};

const RegisterPage = () => {
  return <Register />;
};

export default RegisterPage;
