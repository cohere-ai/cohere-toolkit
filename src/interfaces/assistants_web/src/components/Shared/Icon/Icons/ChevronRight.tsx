import * as React from 'react';
import { SVGProps } from 'react';

import { cn } from '@/utils';

export const ChevronRight: React.FC<SVGProps<SVGSVGElement>> = ({ className, ...props }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 16 16"
    className={cn('h-full w-full fill-inherit', className)}
    {...props}
  >
    <path
      d="M10.293 8.67976C10.0977 8.87502 9.78116 8.87502 9.5859 8.67976L4.26363 3.3575C4.06837 3.16223 4.06837 2.84565 4.26363 2.65039L4.61719 2.29684C4.81245 2.10158 5.12903 2.10158 5.32429 2.29684L10.6466 7.6191C10.8418 7.81436 10.8418 8.13095 10.6466 8.32621L10.293 8.67976Z"
      fill="inherit"
    />
    <path
      d="M10.293 7.26394C10.0977 7.06868 9.78116 7.06868 9.5859 7.26394L4.26363 12.5862C4.06837 12.7815 4.06837 13.0981 4.26363 13.2933L4.61719 13.6469C4.81245 13.8421 5.12903 13.8421 5.32429 13.6469L10.6466 8.3246C10.8418 8.12934 10.8418 7.81276 10.6466 7.6175L10.293 7.26394Z"
      fill="inherit"
    />
  </svg>
);
