import * as React from 'react';
import { SVGProps } from 'react';

export const Carbon: React.FC<SVGProps<SVGSVGElement>> = ({ className, ...props }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={16}
    height={16}
    fill="none"
    viewBox="0 0 65 64"
    {...props}
  >
    <rect width={63} height={63} x={1} y={0.5} fill="#000" rx={31.5} />
    <path fill="#B5B5B5" d="M15.833 22 32.5 12l16.667 10L32.5 32 15.833 22Z" />
    <path fill="#E0E0E0" d="M15.833 42 32.5 52V32L15.833 22v20Z" />
    <path fill="#5C5C5C" d="M49.167 42.667 32.5 52V32l16.667-10v20.667Z" />
    <rect width={63} height={63} x={1} y={0.5} stroke="#fff" rx={31.5} />
  </svg>
);
