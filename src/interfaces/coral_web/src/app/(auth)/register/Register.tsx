'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { SubmitHandler, useForm } from 'react-hook-form';

import { AuthLink } from '@/components/AuthLink';
import { Button, Input, Text } from '@/components/Shared';
import { useSession } from '@/hooks/session';
import { getQueryString, simpleEmailValidation } from '@/utils';

interface Credentials {
  name: string;
  email: string;
  password: string;
}

type RegisterStatus = 'idle' | 'pending';

/**
 * @description The register page supports creating an account with an email and password.
 */
const Register: React.FC = () => {
  const router = useRouter();
  const search = useSearchParams();

  const { registerMutation } = useSession();

  const registerStatus: RegisterStatus = registerMutation.isPending ? 'pending' : 'idle';
  const { register, handleSubmit, formState } = useForm<Credentials>();

  const onSubmit: SubmitHandler<Credentials> = async (data) => {
    const { name, email, password } = data;
    try {
      await registerMutation.mutateAsync(
        { name, email, password },
        { onSuccess: () => router.push('/login') }
      );
    } catch (error) {
      console.error(error);
    }
  };

  const redirect = getQueryString(search.get('redirect_uri'));

  const errors: string[] = [];

  return (
    <div className="flex flex-col items-center justify-center">
      <Text as="h1" styleAs="h3">
        Create your account
      </Text>

      <form onSubmit={handleSubmit(onSubmit)} className="mt-10 flex w-full flex-col">
        <Input
          className="w-full"
          label="name"
          placeholder="Your Name"
          type="text"
          stackPosition="start"
          hasError={!!formState.errors.name}
          errorText="Please enter a name"
          {...register('name', {
            required: true,
            validate: (value) => !!value.trim(),
          })}
        />

        <Input
          className="w-full"
          label="Email"
          placeholder="yourname@email.com"
          type="email"
          stackPosition="center"
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
              <Text key={error} className="mt-4 text-danger-350 first-letter:uppercase">
                {error}
              </Text>
            )
        )}

        <Button
          disabled={registerStatus === 'pending' || !formState.isValid}
          label={registerStatus === 'pending' ? 'Logging in...' : 'Sign up'}
          type="submit"
          className="mt-10 w-full self-center md:w-fit"
          splitIcon="arrow-right"
        />
      </form>

      <Text as="div" className="mt-10 flex w-full items-center justify-between text-volcanic-400">
        Already have an account?
        <AuthLink
          redirect={redirect !== '/' ? redirect : undefined}
          action="login"
          className="text-green-250 no-underline"
        />
      </Text>
    </div>
  );
};

export default Register;
