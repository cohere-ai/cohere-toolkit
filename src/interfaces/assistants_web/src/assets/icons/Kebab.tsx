import * as React from 'react';
import { SVGProps } from 'react';

import { cn } from '@/utils';

export const Kebab: React.FC<SVGProps<SVGSVGElement>> = ({ className, ...props }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 16 16"
    className={cn('h-full w-full fill-inherit', className)}
    {...props}
  >
    <path
      d="M7 3.5C7 3.22386 7.22386 3 7.5 3H8.5C8.77614 3 9 3.22386 9 3.5V4.5C9 4.77614 8.77614 5 8.5 5H7.5C7.22386 5 7 4.77614 7 4.5V3.5Z"
      fill="inherit"
    />
    <path
      d="M7 7.5C7 7.22386 7.22386 7 7.5 7H8.5C8.77614 7 9 7.22386 9 7.5V8.5C9 8.77614 8.77614 9 8.5 9H7.5C7.22386 9 7 8.77614 7 8.5V7.5Z"
      fill="inherit"
    />
    <path
      d="M7 11.5C7 11.2239 7.22386 11 7.5 11H8.5C8.77614 11 9 11.2239 9 11.5V12.5C9 12.7761 8.77614 13 8.5 13H7.5C7.22386 13 7 12.7761 7 12.5V11.5Z"
      fill="inherit"
    />
  </svg>
);
