import { QueryClient, dehydrate } from '@tanstack/react-query';
import { GetServerSideProps, NextPage } from 'next';
import { useRouter } from 'next/router';
import { useMemo, useState } from 'react';
import { SubmitHandler, useForm } from 'react-hook-form';

<<<<<<< HEAD
import { CohereClient, CohereUnauthorizedError } from '@/cohere-client';
import { AuthLink } from '@/components/AuthLink';
=======
import { CohereClient, CohereUnauthorizedError, ListAuthStrategy } from '@/cohere-client';
>>>>>>> main
import { Button, Input, Text } from '@/components/Shared';
import { OidcSSOButton } from '@/components/Welcome/OidcSSOButton';
import { WelcomePage } from '@/components/WelcomePage';
import { useAuthConfig } from '@/hooks/authConfig';
import { useOidcAuthRoute } from '@/hooks/oidcAuthRoute';
import { useSession } from '@/hooks/session';
import { useNotify } from '@/hooks/toast';
import { PageAppProps, appSSR } from '@/pages/_app';
<<<<<<< HEAD
=======
import type { NoNullProperties } from '@/types/util';
>>>>>>> main
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
<<<<<<< HEAD
  const { login: authStrategies } = useAuthConfig();
  const { oidcAuth } = useOidcAuthRoute();

  const notify = useNotify();
  const loginStatus: LoginStatus = loginMutation.isLoading ? 'pending' : 'idle';

  const { register, handleSubmit, formState } = useForm<Credentials>();
  const redirect = getQueryString(router.query.redirect_uri);
  const hasBasicAuth = authStrategies.some((login) => login.strategy.toLowerCase() === 'basic');
  const ssoStrategies = useMemo(() => {
    return authStrategies ? authStrategies.filter((strategy) => strategy.strategy !== 'Basic') : [];
  }, [authStrategies]);
=======
  const { loginStrategies } = useAuthConfig();
  const { oidcAuth } = useOidcAuthRoute();

  const notify = useNotify();
  const loginStatus: LoginStatus = loginMutation.isPending ? 'pending' : 'idle';

  const { register, handleSubmit, formState } = useForm<Credentials>();
  const redirect = getQueryString(router.query.redirect_uri);
  const hasBasicAuth = loginStrategies.some((login) => login.strategy.toLowerCase() === 'basic');
  const ssoStrategies = useMemo(() => {
    return (
      loginStrategies
        ? loginStrategies.filter(
            (strategy) =>
              strategy.strategy !== 'Basic' &&
              strategy.client_id !== null &&
              strategy.authorization_endpoint !== null
          )
        : []
    ) as NoNullProperties<ListAuthStrategy>[];
  }, [loginStrategies]);
>>>>>>> main
  const [errors, setErrors] = useState<string[]>([]);

  const onSubmit: SubmitHandler<Credentials> = async (data) => {
    const { email, password } = data;
    try {
      await loginMutation.mutate(
        { email, password },
        {
          onSuccess: () => {
            router.push(redirect || '/');
          },
          onError: (error) => {
            if (error instanceof CohereUnauthorizedError) {
              setErrors([...errors, 'Invalid email or password']);
            }
          },
        }
      );
    } catch (error) {
      console.error(error);
      notify.error('An error occurred while logging in');
    }
  };

<<<<<<< HEAD
  const oidcAuthStart = (strategy: string, authorizationEndpoint: string) => {
=======
  const oidcAuthStart = (strategy: string, authorizationEndpoint: string, pkceEnabled: boolean) => {
>>>>>>> main
    oidcAuth.start({
      redirect,
      strategy,
      authorizationEndpoint,
<<<<<<< HEAD
=======
      pkceEnabled,
>>>>>>> main
    });
  };

  return (
<<<<<<< HEAD
    <WelcomePage title="Login" navigationAction="register">
=======
    <WelcomePage title="Login">
>>>>>>> main
      <div className="flex flex-col items-center justify-center">
        <Text
          as="h1"
          styleAs="h3"
          onClick={() => {
            console.warn('Clicked title');
            errors.push('Clicked title');
          }}
        >
          Log in
        </Text>
        <div className="mt-10 flex w-full flex-col items-center gap-1">
          {ssoStrategies.map((ssoConfig) => (
            <OidcSSOButton
              key={ssoConfig.strategy}
              className="inline-flex w-full flex-auto"
              service={ssoConfig.strategy}
<<<<<<< HEAD
              onClick={() => oidcAuthStart(ssoConfig.strategy, ssoConfig.authorization_endpoint)}
=======
              onClick={() =>
                oidcAuthStart(
                  ssoConfig.strategy,
                  ssoConfig.authorization_endpoint,
                  ssoConfig.pkce_enabled
                )
              }
>>>>>>> main
            />
          ))}
        </div>

        {hasBasicAuth && (
          <form
            onSubmit={handleSubmit(onSubmit)}
            onChange={() => setErrors([])}
            className="mt-10 flex w-full flex-col"
          >
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
        )}
<<<<<<< HEAD

        <Text as="div" className="mt-10 flex w-full items-center justify-between text-volcanic-700">
          New user?
          <AuthLink
            redirect={redirect !== '/' ? redirect : undefined}
            action="register"
            className="text-green-700 no-underline"
          />
        </Text>
=======
>>>>>>> main
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
