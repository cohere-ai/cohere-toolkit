import * as React from 'react';
import { SVGProps } from 'react';

import { cn } from '@/utils';

export const Edit: React.FC<SVGProps<SVGSVGElement>> = ({ className, ...props }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 16 16"
    className={cn('h-full w-full fill-inherit', className)}
    {...props}
  >
    <path
      d="M9.84157 7.6959C9.92126 7.6162 9.95879 7.50363 9.94285 7.39206L9.68511 5.58789C9.64338 5.29579 9.28608 5.17669 9.07743 5.38534L2.08652 12.3762C2.01576 12.447 2.01576 12.5617 2.08652 12.6325L3.36764 13.9136C3.4384 13.9844 3.55311 13.9844 3.62387 13.9136L9.84157 7.6959Z"
      fill="inherit"
    />
    <path
      d="M2.65612 14.4841C2.74853 14.5765 2.71401 14.7336 2.59137 14.7787L1.14857 15.3099C0.86198 15.4154 0.58333 15.1367 0.688837 14.8501L1.21999 13.4073C1.26514 13.2847 1.4222 13.2502 1.51461 13.3426L2.65612 14.4841Z"
      fill="inherit"
    />
  </svg>
);
