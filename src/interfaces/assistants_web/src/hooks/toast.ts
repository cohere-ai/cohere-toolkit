import { toast } from 'sonner';

export const useNotify = () => {
  const error = (message: string) =>
    toast.error(message, {
      duration: Infinity,
      cancel: { label: 'x', onClick: () => toast.dismiss() },
    });
  const info = (message: string) => toast.info(message, { duration: 5000 });
  const success = (message: string) => toast.success(message, { duration: 5000 });
  const loading = (message: string) => toast.loading(message);

  const dismiss = (id: string | number) => toast.dismiss(id);

  return { error, info, success, loading, dismiss };
};
