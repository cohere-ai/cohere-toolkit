'use client';

import { usePathname } from 'next/navigation';
import { PropsWithChildren } from 'react';

import { AuthLink } from '@/components/AuthLink';
import { NavigationUserMenu } from '@/components/NavigationUserMenu';
import { Text } from '@/components/Shared';
import { CellBackground } from '@/components/Welcome/CellBackground';
import { Navigation } from '@/components/Welcome/Navigation';

type Props = PropsWithChildren<{
  userEmail?: string;
  videoStep?: number;
  showEmailInHeader?: boolean;
}>;

export const WelcomePage: React.FC<Props> = ({
  children,
  userEmail,
  videoStep = 0,
  showEmailInHeader,
}) => {
  const pathname = usePathname();
  const navigationAction = pathname.includes('/login')
    ? 'register'
    : pathname.includes('/register')
    ? 'login'
    : undefined;
  return (
    <div className="relative flex h-full min-h-screen w-full bg-green-950">
      <CellBackground step={videoStep} />

      <div className="max-w-page relative mx-auto flex h-full min-h-screen w-full flex-col overflow-y-auto">
        <Navigation className="max-w-page top-0 w-full md:fixed">
          {userEmail && <NavigationUserMenu userEmail={userEmail} showEmail={showEmailInHeader} />}
          {!userEmail && navigationAction && (
            <Text styleAs="p-lg" as="span" className="capitalize">
              <AuthLink action={navigationAction} className="no-underline" />
            </Text>
          )}
        </Navigation>

        <div className="my-auto w-full px-6 pb-6 md:mx-auto md:w-fit md:px-0 md:py-4">
          <div className="flex w-full flex-col rounded-lg border border-marble-950 bg-white p-6 md:w-modal md:p-10">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
};
