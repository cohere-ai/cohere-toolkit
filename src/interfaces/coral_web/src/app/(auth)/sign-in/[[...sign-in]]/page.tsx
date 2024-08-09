import React from 'react';
import { SignIn } from '@clerk/nextjs';
const SignInPage = () => {
  return (
    <div className='flex flex-row justify-center mt-12'>
      <SignIn />
    </div>
  );
};

export default SignInPage;
