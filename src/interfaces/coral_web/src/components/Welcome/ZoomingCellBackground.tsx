import { useState } from 'react';

import { useDeviceType } from '@/hooks/deviceType';
import { cn } from '@/utils';

type Props = {
  step: number;
};

/**
 * This component is in charge of rendering the cell background of all the welcome pages.
 * It will load in a video and animate during the KYC flow on desktop, otherwise, it will show a static image.
 */
export const ZoomingCellBackground: React.FC<Props> = ({ step = 0 }) => {
  const { isMobile, isDesktop } = useDeviceType();
  const [isVideoError, setIsVideoError] = useState(false);

  const handleVideoError = () => {
    setIsVideoError(true);
  };

  return (
    <div
      className={cn('absolute z-0 h-full w-full overflow-hidden', {
        "mx-auto bg-[url('/images/kycCellBackground.png')] bg-contain bg-no-repeat lg:bg-cover":
          step === 0 || isVideoError || isMobile,
      })}
    >
      {isDesktop && step > 0 && (
        <video
          preload="auto"
          autoPlay
          muted
          loop
          className={cn(
            'h-full w-full object-cover',
            'transition-transform duration-300 ease-in-out',
            {
              'scale-100': step === 1,
              'scale-125': step === 2,
              'scale-175': step === 3,
            }
          )}
          onError={handleVideoError}
        >
          <source src="/videos/KYC_BG_5K.mp4" type="video/mp4" />
        </video>
      )}
    </div>
  );
};
