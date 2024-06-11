import { QueryClient, dehydrate } from '@tanstack/react-query';
import { GetServerSideProps, NextPage } from 'next';
import { useRouter } from 'next/router';
import { useEffect } from 'react';

import { CohereClient } from '@/cohere-client';
import { Text } from '@/components/Shared';
import { WelcomePage } from '@/components/WelcomePage';
import { useSession } from '@/hooks/session';
import { PageAppProps, appSSR } from '@/pages/_app';
import { getQueryString } from '@/utils';

type Props = PageAppProps & {};

/**
 * @description The login page supports logging in with an email and password.
 */
const CompleteOauthPage: NextPage<Props> = () => {
  const router = useRouter();
  const { googleSSOMutation } = useSession();
  const redirect = getQueryString(router.query.redirect_uri);

  useEffect(() => {
    googleSSOMutation.mutate({
      code: router.query.code as string,
    },
    {
      onSuccess: () => {
        router.push(redirect || '/');
      },
      onError: () => {
        router.push('/login');
      }
    });
  }, []);

  return (
    <WelcomePage title="Login">
      <div className="flex flex-col items-center justify-center">
        <Text as="h1" styleAs="h3">
          Logging in
        </Text>
      </div>
    </WelcomePage>
  );
};

export const getServerSideProps: GetServerSideProps<Props> = async () => {
  const deps = appSSR.initialize() as {
    queryClient: QueryClient;
    cohereClient: CohereClient;
  };

  return {
    props: {
      appProps: {
        reactQueryState: dehydrate(deps.queryClient),
      },
    },
  };
};

export default CompleteOauthPage;
