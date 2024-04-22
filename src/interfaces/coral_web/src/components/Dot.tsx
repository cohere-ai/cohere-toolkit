import { SVGProps } from 'react';

import { cn } from '@/utils';

type Props = {
  on: boolean;
} & SVGProps<SVGSVGElement>;

export const Dot: React.FC<Props> = ({ on, className, ...props }) => {
  return (
    <span className={cn('relative flex', className)}>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="9"
        height="9"
        viewBox="0 0 9 9"
        className={cn('inline-flex', {
          'fill-primary-300': on,
          'fill-marble-500': !on,
        })}
        {...props}
      >
        <circle cx="4.5" cy="4.5" r="4.5" />
      </svg>
      {on && (
        <span className="absolute inline-flex h-full w-full animate-ping-once rounded-full bg-primary-300 opacity-75" />
      )}
    </span>
  );
};
