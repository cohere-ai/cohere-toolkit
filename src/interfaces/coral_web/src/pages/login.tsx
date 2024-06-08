import { QueryClient, dehydrate } from '@tanstack/react-query';
import { GetServerSideProps, NextPage } from 'next';
import { useRouter } from 'next/router';
import { SubmitHandler, useForm } from 'react-hook-form';

import { CohereClient } from '@/cohere-client';
import { AuthLink } from '@/components/AuthLink';
import { Button, Input, Text } from '@/components/Shared';
// import { GoogleSSOButton } from '@/components/Welcome/GoogleSSOButton';
import { WelcomePage } from '@/components/WelcomePage';
// import { useGoogleAuthRoute } from '@/hooks/googleAuthRoute';
import { useSession } from '@/hooks/session';
import { PageAppProps, appSSR } from '@/pages/_app';
import { getQueryString, simpleEmailValidation } from '@/utils';

interface Credentials {
  email: string;
  password: string;
}

type Props = PageAppProps & {};

type LoginStatus = 'idle' | 'pending';

/**
 * @description The login page supports logging in with an email and password.
 */
const LoginPage: NextPage<Props> = () => {
  const router = useRouter();
  const { loginMutation } = useSession();

  const loginStatus: LoginStatus = loginMutation.isLoading ? 'pending' : 'idle';

  const { register, handleSubmit, formState } = useForm<Credentials>();
  const redirect = getQueryString(router.query.redirect_uri);
  const errors: string[] = [];

  const onSubmit: SubmitHandler<Credentials> = async (data) => {
    const { email, password } = data;
    try {
      await loginMutation.mutate(
        { email, password },
        {
          onSuccess: () => {
            router.push(redirect || '/');
          },
        }
      );
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <WelcomePage title="Login" navigationAction="register">
      <div className="flex flex-col items-center justify-center">
        <Text as="h1" styleAs="h3">
          Log in
        </Text>
        {/* <div className="mt-10 flex w-full flex-col items-center gap-1 sm:h-10 sm:flex-row">
          <GoogleSSOButton className="inline-flex w-full flex-auto" onClick={googleAuthStart} />
        </div> */}

        <form onSubmit={handleSubmit(onSubmit)} className="mt-10 flex w-full flex-col">
          <Input
            className="w-full"
            label="Email"
            placeholder="yourname@email.com"
            type="email"
            stackPosition="start"
            hasError={!!formState.errors.email}
            errorText="Please enter a valid email address"
            {...register('email', {
              required: true,
              validate: (value) => simpleEmailValidation(value),
            })}
          />

          <Input
            className="mb-2 w-full"
            label="Password"
            placeholder="••••••••••••"
            type="password"
            actionType="revealable"
            stackPosition="end"
            hasError={!!formState.errors.password}
            errorText="Please enter a valid password"
            {...register('password', { required: true })}
          />

          {errors.map(
            (error) =>
              error && (
                <Text key={error} className="mt-4 text-danger-500 first-letter:uppercase">
                  {error}
                </Text>
              )
          )}

          <Button
            disabled={loginStatus === 'pending' || !formState.isValid}
            label={loginStatus === 'pending' ? 'Logging in...' : 'Log in'}
            type="submit"
            className="mt-10 w-full self-center md:w-fit"
            splitIcon="arrow-right"
          />
        </form>

        <Text as="div" className="mt-10 flex w-full items-center justify-between text-volcanic-700">
          New user?
          <AuthLink
            redirect={redirect !== '/' ? redirect : undefined}
            action="register"
            className="text-green-700 no-underline"
          />
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

export default LoginPage;
