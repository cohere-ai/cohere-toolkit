import * as React from 'react';
import { SVGProps } from 'react';

import { cn } from '@/utils';

export const ChevronLeft: React.FC<SVGProps<SVGSVGElement>> = ({ className, ...props }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 16 16"
    className={cn('h-full w-full fill-inherit', className)}
    {...props}
  >
    <path
      d="M4.61719 8.67976C4.81245 8.87502 5.12903 8.87502 5.32429 8.67976L10.6466 3.3575C10.8418 3.16223 10.8418 2.84565 10.6466 2.65039L10.293 2.29684C10.0977 2.10158 9.78116 2.10158 9.5859 2.29684L4.26363 7.6191C4.06837 7.81436 4.06837 8.13095 4.26363 8.32621L4.61719 8.67976Z"
      fill="inherit"
    />
    <path
      d="M4.61719 7.26394C4.81245 7.06868 5.12903 7.06868 5.32429 7.26394L10.6466 12.5862C10.8418 12.7815 10.8418 13.0981 10.6466 13.2933L10.293 13.6469C10.0977 13.8421 9.78116 13.8421 9.5859 13.6469L4.26363 8.3246C4.06837 8.12934 4.06837 7.81276 4.26363 7.6175L4.61719 7.26394Z"
      fill="inherit"
    />
  </svg>
);
