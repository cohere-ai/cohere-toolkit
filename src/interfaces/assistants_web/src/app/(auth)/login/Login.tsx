'use client';

import { useParams, useRouter } from 'next/navigation';
import { useState } from 'react';
import { SubmitHandler, useForm } from 'react-hook-form';

import { CohereUnauthorizedError } from '@/cohere-client';
import { AuthLink } from '@/components/AuthLink';
import { Button, Input, Spinner, Text } from '@/components/Shared';
import { OidcSSOButton } from '@/components/Welcome/OidcSSOButton';
import { useAuthStrategies } from '@/hooks/authStrategies';
import { useOidcAuthRoute } from '@/hooks/oidcAuthRoute';
import { useSession } from '@/hooks/session';
import { useNotify } from '@/hooks/toast';
import { getQueryString, simpleEmailValidation } from '@/utils';

interface Credentials {
  email: string;
  password: string;
}

type LoginStatus = 'idle' | 'pending';

/**
 * @description The login page supports logging in with an email and password.
 */
const Login: React.FC = () => {
  const params = useParams();
  const router = useRouter();
  const { loginMutation } = useSession();
  const { data: authStrategies, isFetching } = useAuthStrategies();
  const { oidcAuth } = useOidcAuthRoute();

  const notify = useNotify();
  const loginStatus: LoginStatus = loginMutation.isPending ? 'pending' : 'idle';

  const { register, handleSubmit, formState } = useForm<Credentials>();
  const redirect = getQueryString(params.redirect_uri);
  const [errors, setErrors] = useState<string[]>([]);

  const onSubmit: SubmitHandler<Credentials> = async (data) => {
    const { email, password } = data;
    try {
      await loginMutation.mutateAsync(
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

  const oidcAuthStart = (strategy: string, authorizationEndpoint: string, pkceEnabled: boolean) => {
    oidcAuth.start({
      redirect,
      strategy,
      authorizationEndpoint,
      pkceEnabled,
    });
  };

  return (
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
        {isFetching ? (
          <Spinner />
        ) : !authStrategies ? (
          <Text>No authentication strategies are configured.</Text>
        ) : authStrategies.ssoStrategies ? (
          authStrategies.ssoStrategies.map((ssoConfig) => (
            <OidcSSOButton
              key={ssoConfig.strategy}
              className="inline-flex w-full flex-auto"
              service={ssoConfig.strategy}
              onClick={() =>
                oidcAuthStart(
                  ssoConfig.strategy,
                  ssoConfig.authorization_endpoint,
                  ssoConfig.pkce_enabled
                )
              }
            />
          ))
        ) : (
          authStrategies.hasBasicAuth && (
            <>
              <form
                onSubmit={handleSubmit(onSubmit)}
                onChange={() => setErrors([])}
                className="mt-10 flex w-full flex-col gap-4"
              >
                <Input
                  className="w-full"
                  label="Email"
                  placeholder="yourname@email.com"
                  type="email"
                  errorText={
                    !!formState.errors.email ? 'Please enter a valid email address' : undefined
                  }
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
                  actionType="reveal"
                  errorText={
                    !!formState.errors.password ? 'Please enter a valid password' : undefined
                  }
                  {...register('password', { required: true })}
                />

                {errors.map(
                  (error) =>
                    error && (
                      <Text key={error} className="mt-4 text-danger-350 first-letter:uppercase">
                        {error}
                      </Text>
                    )
                )}

                <Button
                  disabled={loginStatus === 'pending' || !formState.isValid}
                  label={loginStatus === 'pending' ? 'Logging in...' : 'Log in'}
                  buttonType="submit"
                  kind="cell"
                  theme="evolved-green"
                  iconPosition="end"
                  className="mt-10 w-full self-center md:w-fit"
                />
              </form>

              <Text
                as="div"
                className="mt-10 flex w-full items-center justify-center gap-2 text-volcanic-700"
              >
                New user?
                <AuthLink
                  redirect={redirect !== '/' ? redirect : undefined}
                  action="register"
                  theme="evolved-green"
                />
              </Text>
            </>
          )
        )}
      </div>
    </div>
  );
};

export default Login;
