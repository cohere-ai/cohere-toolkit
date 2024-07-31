import * as React from 'react';
import { SVGProps } from 'react';

import { cn } from '@/utils';

export const Link: React.FC<SVGProps<SVGSVGElement>> = ({ className, ...props }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    className={cn('h-full w-full fill-inherit', className)}
    {...props}
  >
    <path
      fill="#EFEFF5"
      d="M2 8a2.5 2.5 0 0 0 2.5 2.5H7a.5.5 0 0 1 0 1H4.5a3.5 3.5 0 1 1 0-7H7a.5.5 0 1 1 0 1H4.5A2.5 2.5 0 0 0 2 8Zm10.5-3.5H10a.5.5 0 1 0 0 1h2.5a2.5 2.5 0 0 1 0 5H10a.5.5 0 0 0 0 1h2.5a3.5 3.5 0 1 0 0-7Z"
    />
  </svg>
);
