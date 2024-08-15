import * as React from 'react';
import { SVGProps } from 'react';

import { cn } from '@/utils';

export const Close: React.FC<SVGProps<SVGSVGElement>> = ({ className, ...props }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 16 16"
    className={cn('h-full w-full fill-inherit', className)}
    {...props}
  >
    <path
      d="M3.93866 12.4289C4.13393 12.6241 4.4505 12.6241 4.64576 12.4289L12.4429 4.63176C12.6381 4.43649 12.6381 4.1199 12.4429 3.92464L12.0893 3.57109C11.8941 3.37584 11.5775 3.37584 11.3822 3.5711L3.5851 11.3682C3.38983 11.5635 3.38983 11.8801 3.5851 12.0753L3.93866 12.4289Z"
      fill="inherit"
    />
    <path
      d="M12.4429 12.0753C12.6382 11.8801 12.6382 11.5635 12.4429 11.3682L4.64578 3.57109C4.45051 3.37583 4.13392 3.37583 3.93866 3.5711L3.58512 3.92466C3.38986 4.11993 3.38986 4.4365 3.58512 4.63176L11.3822 12.4289C11.5775 12.6241 11.8941 12.6241 12.0894 12.4289L12.4429 12.0753Z"
      fill="inherit"
    />
  </svg>
);
