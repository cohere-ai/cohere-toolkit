import { NextPage } from 'next';
import { Suspense } from 'react';

import OauthCallback from './OauthCallback';

const OauthCallbackPage: NextPage = () => {
  return (
    <Suspense>
      <OauthCallback />
    </Suspense>
  );
};

export default OauthCallbackPage;
