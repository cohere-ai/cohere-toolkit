import * as React from 'react';
import { SVGProps } from 'react';

import { IconKind } from '@/components/Shared/Icon/Icon';
import { cn } from '@/utils';

type Props = {
  kind?: IconKind;
} & SVGProps<SVGSVGElement>;

export const File: React.FC<Props> = ({ className, kind, ...props }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 16 16"
    className={cn('h-full w-full fill-inherit', className)}
    {...props}
  >
    {kind === 'default' ? (
      <>
        <path
          d="M7.5 0.5V4.50004C7.5 5.60461 8.39543 6.50004 9.5 6.50004H13.5V14C13.5 14.8284 12.8284 15.5 12 15.5H4C3.17157 15.5 2.5 14.8284 2.5 14V2C2.5 1.17157 3.17157 0.5 4 0.5H7.5Z"
          fill="inherit"
        />
        <path
          d="M8.5 0.504911V4.50004C8.5 5.05233 8.94771 5.50004 9.5 5.50004H13.4951C13.4664 5.14662 13.3132 4.81324 13.0607 4.56066L9.43934 0.93934C9.18677 0.686772 8.85341 0.533575 8.5 0.504911Z"
          fill="inherit"
        />
      </>
    ) : (
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M4.5 1.5C3.94772 1.5 3.5 1.94772 3.5 2.5V13.5C3.5 14.0523 3.94772 14.5 4.5 14.5H11.5C12.0523 14.5 12.5 14.0523 12.5 13.5V6.49998H9.5C8.39543 6.49998 7.5 5.60455 7.5 4.49998V1.5H4.5ZM8.5 1.51948V4.49998C8.5 5.05227 8.94772 5.49998 9.5 5.49998H12.4054C12.3614 5.4063 12.3029 5.31921 12.231 5.24226L9.03457 1.81766C8.89081 1.66365 8.70338 1.56024 8.5 1.51948ZM2.5 2.5C2.5 1.39543 3.39543 0.5 4.5 0.5H8.30353C8.85787 0.5 9.38735 0.730078 9.7656 1.13532L12.9621 4.55993C13.3077 4.93027 13.5 5.418 13.5 5.9246V13.5C13.5 14.6046 12.6046 15.5 11.5 15.5H4.5C3.39543 15.5 2.5 14.6046 2.5 13.5V2.5Z"
        fill="inherit"
      />
    )}
  </svg>
);
