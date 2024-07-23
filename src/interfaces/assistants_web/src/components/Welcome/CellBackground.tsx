'use client';

import { useState } from 'react';

import { cn } from '@/utils';

type Props = {
  step: number;
};

/**
 * This component is in charge of rendering the cell background of all the welcome pages.
 * It will load in a video and animate during the KYC flow on desktop, otherwise, it will show a static image.
 */
export const CellBackground: React.FC<Props> = ({ step = 0 }) => {
  return (
    <div
      className={cn(
        'absolute z-0 h-full w-full overflow-hidden',
        "mx-auto bg-[url('/images/kycCellBackground.png')] bg-contain bg-no-repeat lg:bg-cover"
      )}
    />
  );
};
