import * as React from 'react';
import { SVGProps } from 'react';

import { cn } from '@/utils';

export const Checkmark: React.FC<SVGProps<SVGSVGElement>> = ({ className, ...props }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 16 16"
    className={cn('h-full w-full fill-inherit', className)}
    {...props}
  >
    <path
      d="M14.159 1.09261C13.9746 0.944001 13.71 0.977804 13.5654 1.16844L4.22651 13.4792C4.10501 13.6394 4.10384 13.8654 4.22367 14.0269L4.81783 14.8278C4.98764 15.0567 5.31845 15.0575 5.48935 14.8295L14.9096 2.26231C15.0551 2.06823 15.0214 1.78762 14.8345 1.63703L14.159 1.09261Z"
      fill="inherit"
    />
    <path
      d="M1.16774 9.10429C0.980777 9.2529 0.94463 9.53159 1.087 9.72675L4.32487 14.1652C4.46724 14.3604 4.73421 14.3981 4.92117 14.2495L5.59821 13.7113C5.78517 13.5627 5.82132 13.284 5.67895 13.0888L2.44108 8.65039C2.29871 8.45523 2.03173 8.4175 1.84478 8.56611L1.16774 9.10429Z"
      fill="inherit"
    />
  </svg>
);
