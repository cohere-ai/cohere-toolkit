import { QueryClient, dehydrate } from '@tanstack/react-query';
import { GetServerSideProps, NextPage } from 'next';
import { useRouter } from 'next/router';
// import { useGoogleReCaptcha } from 'react-google-recaptcha-v3';
import { SubmitHandler, useForm } from 'react-hook-form';

import { CohereClient } from '@/cohere-client';
import { AuthLink } from '@/components/AuthLink';
import { Button, InlineLink, Input, Text } from '@/components/Shared';
import { GithubSSOButton } from '@/components/Welcome/GithubSSOButton';
import { GoogleSSOButton } from '@/components/Welcome/GoogleSSOButton';
import { WelcomePage } from '@/components/WelcomePage';
import { useGithubAuthRoute } from '@/hooks/githubAuthRoute';
import { useGoogleAuthRoute } from '@/hooks/googleAuthRoute';
import { PageAppProps, appSSR } from '@/pages/_app';
import { getQueryString, simpleEmailValidation } from '@/utils';

interface Credentials {
  email: string;
  password: string;
}

type Props = PageAppProps & {};

/**
 * @description The login page supports logging in with an email and password, with Google SSO, and with Github SSO.
 */
const LoginPage: NextPage<Props> = (props) => {
  const router = useRouter();
  // session returns a user object that includes fields like: email, name, avatar url,
  // if they have google/github/email auth enabled, etc.
  // const { session } = useSession();

  // const { executeRecaptcha } = useGoogleReCaptcha();
  const { googleAuth } = useGoogleAuthRoute();

  const googleAuthStart = async () => {
    // const googleRecaptchaToken = await executeRecaptcha?.(RecaptchaAction.AUTH_GOOGLE);
    const googleRecaptchaToken = '';
    googleAuth.start({
      redirect,
      recaptchaToken: googleRecaptchaToken,
    });
  };

  const { githubAuth } = useGithubAuthRoute();

  const githubAuthStart = async () => {
    // const githubRecaptchaToken = await executeRecaptcha?.(RecaptchaAction.AUTH_GITHUB);
    const githubRecaptchaToken = '';
    githubAuth.start({
      redirect,
      recaptchaToken: githubRecaptchaToken,
    });
  };

  const { register, handleSubmit, formState } = useForm<Credentials>();

  const onSubmit: SubmitHandler<Credentials> = async (data) => {};

  const redirect = getQueryString(router.query.redirect_uri);

  const errors: string[] = [];

  return (
    <WelcomePage title="Login" navigationAction="register">
      <div className="flex flex-col items-center justify-center">
        <Text as="h1" styleAs="h3">
          Log in
        </Text>
        <div className="mt-10 flex w-full flex-col items-center gap-1 sm:h-10 sm:flex-row">
          <GoogleSSOButton className="inline-flex w-full flex-auto" onClick={googleAuthStart} />
          <GithubSSOButton className="inline-flex w-full flex-auto" onClick={githubAuthStart} />
        </div>

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

          <InlineLink
            label={
              <Text styleAs="p-lg" as="span" className="text-green-700 hover:text-green-900">
                Forgot Password
              </Text>
            }
            href="/reset-password"
            className="flex w-fit self-end no-underline"
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
            disabled={loginStatus === 'pending'}
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
