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
          cancelButton: '!text-volcanic-900 !text-p !ml-auto',
          loading: 'border-quartz-700 border bg-quartz-50 text-volcanic-900',
          success: 'border-success-200 border bg-success-50 text-success-500',
          error: 'border-danger-200 border bg-danger-50 text-danger-500',
          info: 'border-secondary-200 border bg-secondary-50 text-secondary-900',
        },
      }}
      pauseWhenPageIsHidden
      loadingIcon={<Spinner className="h-4 w-4 text-quartz-600" />}
    />
  );
};
