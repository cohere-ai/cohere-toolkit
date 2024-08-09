import React from 'react';
import { SignUp } from '@clerk/nextjs';
const SignUpPage = () => {
  return (
    <div className='flex flex-row justify-center mt-12'>
      <SignUp />
    </div>
  );
};

export default SignUpPage;
