'use client';

import Link from 'next/link';

import { Logo } from '@/components/Shared';
import { cn } from '@/utils';

/**
 * Navigation for the registration, login and onboarding flow.
 */
export const Navigation: React.FC<{
  className?: string;
  children?: React.ReactNode;
}> = ({ className = '', children }) => {
  return (
    <div className={cn('flex items-center justify-between px-7 py-6', className)}>
      <Link href="/" className="w-fit">
        <Logo className="w-24" />
      </Link>

      {children}
    </div>
  );
};
