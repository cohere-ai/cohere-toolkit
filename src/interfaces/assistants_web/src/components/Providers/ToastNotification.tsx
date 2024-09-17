'use client';

import { Toaster } from 'sonner';

import { Icon, STYLE_LEVEL_TO_CLASSES } from '@/components/UI';
import { cn } from '@/utils';

type Props = {
  position?:
    | 'top-left'
    | 'top-right'
    | 'bottom-left'
    | 'bottom-right'
    | 'top-center'
    | 'bottom-center';
};

export const ToastNotification: React.FC<Props> = ({ position = 'bottom-right' }) => {
  return (
    <Toaster
      visibleToasts={9}
      position={position}
      toastOptions={{
        unstyled: true,
        className: cn(
          STYLE_LEVEL_TO_CLASSES.p,
          'w-toast-sm md:w-toast flex items-start gap-x-3 p-3 rounded-lg shadow-xl'
        ),
        cancelButtonStyle: {
          backgroundColor: 'transparent',
          margin: '0',
          padding: '0',
          alignItems: 'center',
          accentColor: 'white',
        },
        classNames: {
          cancelButton: '!text-volcanic-60 dark:!text-marble-950 !text-p-lg !ml-auto',
          error: 'bg-mushroom-800 text-volcanic-60 dark:bg-volcanic-300 dark:text-marble-950',
          info: 'bg-mushroom-600 text-volcanic-60',
        },
      }}
      pauseWhenPageIsHidden
      icons={{
        error: (
          <Icon
            name="information"
            kind="outline"
            className="h-4 w-4 fill-danger-350 dark:fill-danger-500"
          />
        ),
        info: (
          <Icon name="information" className="h-4 w-4 fill-volcanic-60 dark:fill-volcanic-60" />
        ),
      }}
    />
  );
};
