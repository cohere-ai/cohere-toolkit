import * as React from 'react';
import { SVGProps } from 'react';

import { cn } from '@/utils';

export const Subtract: React.FC<SVGProps<SVGSVGElement>> = ({ className, ...props }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 16 16"
    className={cn('h-full w-full fill-inherit', className)}
    {...props}
  >
    <path
      d="M2.00001 8.25001C2.00002 8.52615 2.22387 8.75 2.50001 8.75H13.5268C13.8029 8.75 14.0268 8.52614 14.0268 8.24999L14.0268 7.74999C14.0268 7.47385 13.8029 7.25 13.5268 7.25H2.5C2.22385 7.25 1.99999 7.47386 2 7.75001L2.00001 8.25001Z"
      fill="inherit"
    />
  </svg>
);
