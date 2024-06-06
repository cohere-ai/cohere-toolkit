import { QueryClient, dehydrate } from '@tanstack/react-query';
import { GetServerSideProps, NextPage } from 'next';
import { useRouter } from 'next/router';

import { CohereClient } from '@/cohere-client';
import { Text } from '@/components/Shared';
import { WelcomePage } from '@/components/WelcomePage';
import { useSession } from '@/hooks/session';
import { PageAppProps, appSSR } from '@/pages/_app';
import { useEffect } from 'react';

type Props = PageAppProps & {};

/**
 * @description The login page supports logging in with an email and password.
 */
const LoginPage: NextPage<Props> = (props) => {
  const router = useRouter();
  const { logoutMutation } = useSession();

  useEffect(() => {
    logoutMutation.mutate();
    router.push('/login');
  }, [logoutMutation, router]);

  return (
    <WelcomePage title="Logout" navigationAction="login">
      <div className="flex flex-col items-center justify-center">
        <Text as="h1" styleAs="h3">
          Log out
        </Text>
      </div>
    </WelcomePage>
  );
};

export const getServerSideProps: GetServerSideProps<Props> = async (context) => {
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

export default LoginPage;
