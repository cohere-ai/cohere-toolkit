'use client';

import { useState } from 'react';

import { useIsDesktop } from '@/hooks/breakpoint';
import { cn } from '@/utils';

export const CellBackground: React.FC = () => {
  const isDesktop = useIsDesktop();
  const [isVideoError, setIsVideoError] = useState(false);

  const handleVideoError = () => {
    setIsVideoError(true);
  };
  return (
    <div
      className={cn('absolute z-0 h-full w-full overflow-hidden', {
        "mx-auto bg-[url('/images/kycCellBackground.png')] bg-contain bg-no-repeat lg:bg-cover":
          isVideoError || !isDesktop,
      })}
    >
      {isDesktop && (
        <video
          preload="auto"
          autoPlay
          muted
          loop
          className={cn(
            'h-full w-full scale-100 object-cover',
            'transition-transform duration-300 ease-in-out'
          )}
          onError={handleVideoError}
        >
          <source src="/videos/KYC_BG_5K.mp4" type="video/mp4" />
        </video>
      )}
    </div>
  );
};
