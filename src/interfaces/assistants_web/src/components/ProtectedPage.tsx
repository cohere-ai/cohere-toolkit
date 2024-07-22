'use client';

import { Spinner } from '@/components/Shared';
import { useSession } from '@/hooks/session';

/**
 * @description A component that wraps a page and ensures that the user is authenticated before rendering the page.
 */
export const ProtectedPage: React.FC<React.PropsWithChildren> = ({ children }) => {
  const { isLoading, isLoggedIn } = useSession();

  if (isLoading || !isLoggedIn) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-mushroom-950">
        <Spinner className="h-10 w-10" />
      </div>
    );
  }

  return children;
};
