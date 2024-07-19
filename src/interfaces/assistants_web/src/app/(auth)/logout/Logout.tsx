'use client';

import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

import { Text } from '@/components/Shared';
import { useSession } from '@/hooks/session';

/**
 * @description The login page supports logging in with an email and password.
 */
const Logout = () => {
  const router = useRouter();
  const { logoutMutation } = useSession();

  useEffect(() => {
    logoutMutation.mutate(undefined, {
      onSettled: () => {
        router.push('/login');
      },
    });
  }, []);

  return (
    <div className="flex flex-col items-center justify-center">
      <Text as="h1" styleAs="h3">
        Logging out
      </Text>
    </div>
  );
};

export default Logout;
