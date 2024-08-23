import * as React from 'react';
import { SVGProps } from 'react';

import { cn } from '@/utils';

export const ChevronDown: React.FC<SVGProps<SVGSVGElement>> = ({ className, ...props }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 16 16"
    className={cn('h-full w-full fill-inherit', className)}
    {...props}
  >
    <path
      d="M7.29129 11.8047C7.09603 11.6095 7.09603 11.2929 7.29129 11.0976L12.6136 5.77535C12.8088 5.58009 13.1254 5.58009 13.3207 5.77535L13.6742 6.12891C13.8695 6.32417 13.8695 6.64075 13.6742 6.83601L8.35195 12.1583C8.15669 12.3535 7.8401 12.3535 7.64484 12.1583L7.29129 11.8047Z"
      fill="inherit"
    />
    <path
      d="M8.70711 11.8047C8.90237 11.6095 8.90237 11.2929 8.70711 11.0976L3.38484 5.77535C3.18958 5.58009 2.873 5.58009 2.67773 5.77535L2.32418 6.12891C2.12892 6.32417 2.12892 6.64075 2.32418 6.83601L7.64645 12.1583C7.84171 12.3535 8.15829 12.3535 8.35355 12.1583L8.70711 11.8047Z"
      fill="inherit"
    />
  </svg>
);
