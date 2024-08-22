import * as React from 'react';
import { SVGProps } from 'react';

import { cn } from '@/utils';

export const ChevronUp: React.FC<SVGProps<SVGSVGElement>> = ({ className, ...props }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 16 16"
    className={cn('h-full w-full fill-inherit', className)}
    {...props}
  >
    <path
      d="M7.29129 5.15625C7.09603 5.35151 7.09603 5.66809 7.29129 5.86336L12.6136 11.1856C12.8088 11.3809 13.1254 11.3809 13.3207 11.1856L13.6742 10.8321C13.8695 10.6368 13.8695 10.3202 13.6742 10.125L8.35195 4.8027C8.15669 4.60743 7.8401 4.60743 7.64484 4.8027L7.29129 5.15625Z"
      fill="inherit"
    />
    <path
      d="M8.70711 5.15625C8.90237 5.35151 8.90237 5.66809 8.70711 5.86336L3.38484 11.1856C3.18958 11.3809 2.873 11.3809 2.67773 11.1856L2.32418 10.8321C2.12892 10.6368 2.12892 10.3202 2.32418 10.125L7.64645 4.8027C7.84171 4.60743 8.15829 4.60743 8.35355 4.8027L8.70711 5.15625Z"
      fill="inherit"
    />
  </svg>
);
