'use client';

import { Text } from '@/components/Shared';
import { cn } from '@/utils';

type Props = {
  children?: React.ReactNode;
  className?: string;
};

export const Banner: React.FC<Props> = ({ className = '', children }) => {
  return (
    <Text
      as="div"
      className={cn(
        'rounded-lg border p-4',
        'dark:border-volcanic-300 dark:bg-volcanic-150 dark:text-marble-800',
        'border-mushroom-500 bg-mushroom-800 text-mushroom-200',
        className
      )}
    >
      {children}
    </Text>
  );
};
