'use client';

import { Toaster } from 'sonner';

import { cn } from '@/utils';

import { Icon, STYLE_LEVEL_TO_CLASSES, Spinner } from '..';

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
          'w-toast-sm md:w-toast flex items-start gap-x-3 p-3 rounded-lg'
        ),
        cancelButtonStyle: {
          backgroundColor: 'transparent',
          margin: '0',
          padding: '0',
          alignItems: 'center',
        },
        classNames: {
          cancelButton: '!text-volcanic-60 !text-p-lg !ml-auto',
          loading: 'bg-quartz-600 text-volcanic-60',
          success: 'bg-success-300 text-volcanic-60',
          error: 'bg-danger-350 text-volcanic-60',
          info: 'bg-mushroom-600 text-volcanic-60',
        },
      }}
      pauseWhenPageIsHidden
      icons={{
        success: (
          <Icon name="thumbs-up" className="h-4 w-4 fill-volcanic-60 dark:fill-volcanic-60" />
        ),
        error: (
          <Icon name="thumbs-down" className="h-4 w-4 fill-volcanic-60 dark:fill-volcanic-60" />
        ),
        loading: <Spinner className="h-4 w-4 text-volcanic-60" />,
        info: (
          <Icon name="information" className="h-4 w-4 fill-volcanic-60 dark:fill-volcanic-60" />
        ),
      }}
    />
  );
};
