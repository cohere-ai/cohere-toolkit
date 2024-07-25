'use client';

import { cn } from '@/utils';

export const Skeleton = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => {
  return <div className={cn('animate-pulse rounded-md bg-marble-950', className)} {...props} />;
};
