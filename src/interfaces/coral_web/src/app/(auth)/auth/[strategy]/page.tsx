import { NextPage } from 'next';
import { Suspense } from 'react';

import CompleteOauth from './CompleteOauth';

const CompleteOauthPage: NextPage = () => {
  return (
    <Suspense>
      <CompleteOauth />
    </Suspense>
  );
};

export default CompleteOauthPage;
