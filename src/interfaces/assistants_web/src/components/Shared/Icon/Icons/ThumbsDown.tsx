import * as React from 'react';
import { SVGProps } from 'react';

import { IconKind } from '@/components/Shared/Icon/Icon';
import { cn } from '@/utils';

type Props = {
  kind?: IconKind;
} & SVGProps<SVGSVGElement>;

export const ThumbsDown: React.FC<Props> = ({ className, kind, ...props }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 16 16"
    className={cn('h-full w-full fill-inherit', className)}
    {...props}
  >
    {kind === 'default' ? (
      <>
        <path
          d="M13.5359 10.1657C14.3359 10.1657 15.0359 9.38365 15.0359 8.48993V0.893331C15.0359 0.446472 14.7359 0.111328 14.3359 0.111328H14.2359C13.8359 0.111328 13.6359 0.334758 13.5359 0.781616L11.8359 9.16022C11.7359 9.71879 12.1359 10.1657 12.5359 10.1657H13.5359Z"
          fill="inherit"
        />
        <path
          d="M2.33607 1.78744C2.53607 0.782003 3.33607 0 4.33607 0H11.9361C12.1361 0 12.2361 4.99404e-08 12.3361 0.22343C12.3361 0.335144 12.3361 0.446859 12.3361 0.670288L10.7361 8.82546C10.4361 10.166 9.93607 11.5066 9.23607 12.7355L7.93607 14.9698C7.63607 15.5283 6.93607 15.6401 6.43607 15.4166C5.73607 15.0815 5.73607 14.0761 5.73607 12.9589V11.0598H2.93607C2.33607 11.0598 1.73607 10.7246 1.43607 10.2778C1.03607 9.71918 0.936068 9.04889 1.03607 8.3786L2.33607 1.78744Z"
          fill="inherit"
        />
      </>
    ) : (
      <path
        d="M3.03607 11.1715H6.03607V13.7409C6.03607 14.7463 6.03607 15.1932 6.53607 15.5283C7.03607 15.7518 7.63607 15.6401 8.03607 15.0815L9.33607 12.8472C9.83607 11.9535 10.2361 10.948 10.5361 10.0543H13.7361C14.4361 10.0543 15.0361 9.38404 15.0361 8.60203V1.45229C15.0361 0.670288 14.4361 0 13.7361 0H4.33607C3.43607 0 2.53607 0.782003 2.33607 1.78744L1.03607 8.49032C0.936068 9.16061 1.03607 9.8309 1.43607 10.3895C1.43607 10.3895 2.03607 11.1715 3.03607 11.1715ZM14.0361 8.60203C14.0361 8.71375 13.9361 8.93718 13.7361 8.93718H10.8361L12.4361 1.11715H13.7361C13.9361 1.11715 14.0361 1.22886 14.0361 1.45229V8.60203ZM3.43607 2.01086C3.53607 1.45229 3.93607 1.11715 4.43607 1.11715H11.4361L9.83607 9.16061C9.53607 10.166 9.13607 11.1715 8.63607 12.1769L7.33607 14.4112C7.23607 14.6346 7.03607 14.5229 7.03607 14.4112C7.03607 14.2995 7.03607 13.5175 7.03607 13.0706V10.6129C7.03607 10.2778 6.83607 10.0543 6.53607 10.0543H3.03607C2.73607 10.0543 2.43607 9.94261 2.23607 9.60747C2.03607 9.27232 2.03607 9.04889 2.03607 8.71375L3.43607 2.01086Z"
        fill="inherit"
      />
    )}
  </svg>
);
