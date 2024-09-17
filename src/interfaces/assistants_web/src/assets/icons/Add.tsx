import * as React from 'react';
import { SVGProps } from 'react';

import { cn } from '@/utils';

export const Add: React.FC<SVGProps<SVGSVGElement>> = ({ className, ...props }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 13 14"
    className={cn('h-full w-full fill-inherit', className)}
    {...props}
  >
    <path
      d="M1.01726e-05 7.24972C1.57907e-05 7.52586 0.223872 7.74971 0.50001 7.74971H11.5268C11.8029 7.74971 12.0268 7.52585 12.0268 7.2497L12.0268 6.7497C12.0268 6.47357 11.8029 6.24971 11.5268 6.24971H0.5C0.223854 6.24971 -5.61811e-06 6.47358 1.05748e-10 6.74972L1.01726e-05 7.24972Z"
      fill="inherit"
    />
    <path
      d="M6.26343 13.0131C6.53957 13.0131 6.76342 12.7893 6.76342 12.5131V1.48633C6.76342 1.21018 6.53955 0.986322 6.26341 0.986328L5.76341 0.986338C5.48727 0.986343 5.26342 1.2102 5.26342 1.48634V12.5131C5.26342 12.7893 5.48728 13.0131 5.76343 13.0131L6.26343 13.0131Z"
      fill="inherit"
    />
  </svg>
);
