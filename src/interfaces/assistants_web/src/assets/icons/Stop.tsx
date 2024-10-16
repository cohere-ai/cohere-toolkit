import * as React from 'react';
import { SVGProps } from 'react';

import { cn } from '@/utils';

export const Stop: React.FC<SVGProps<SVGSVGElement>> = ({ className, ...props }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 16 16"
    className={cn('h-full w-full fill-inherit', className)}
    {...props}
  >
    <path
      d="M8 0 C3.582031 0 0 3.582031 0 8 C0 12.417969 3.582031 16 8 16 C12.417969 16 16 12.417969 16 8 C16 3.582031 12.417969 0 8 0 Z M8 14.5 C4.410156 14.5 1.5 11.589844 1.5 8 C1.5 4.410156 4.410156 1.5 8 1.5 C11.589844 1.5 14.5 4.410156 14.5 8 C14.5 11.589844 11.589844 14.5 8 14.5 Z M5 5 L11 5 L11 11 L5 11 Z M5 5"
      fill="inherit"
    />
  </svg>
);
