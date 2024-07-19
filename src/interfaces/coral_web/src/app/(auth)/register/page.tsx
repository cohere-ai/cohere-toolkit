import { Metadata } from 'next';
import { Suspense } from 'react';

import Register from './Register';

export const metadata: Metadata = {
  title: 'Register',
};

const RegisterPage = () => {
  return (
    <Suspense>
      <Register />
    </Suspense>
  );
};

export default RegisterPage;
