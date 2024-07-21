'use client';

import { Toaster } from 'sonner';

import { cn } from '@/utils';

import { STYLE_LEVEL_TO_CLASSES, Spinner } from '..';

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
        },
        classNames: {
          cancelButton: '!text-volcanic-100 !text-p !ml-auto',
          loading: 'border-quartz-700 border bg-quartz-950 text-volcanic-100',
          success: 'border-success-200 border bg-success-950 text-success-200',
          error: '<border-danger-5></border-danger-5>00 border bg-danger-950 text-danger-500',
          info: 'border-mushroom-800 border bg-mushroom-950 text-mushroom-150',
        },
      }}
      pauseWhenPageIsHidden
      loadingIcon={<Spinner className="h-4 w-4 text-quartz-600" />}
    />
  );
};
