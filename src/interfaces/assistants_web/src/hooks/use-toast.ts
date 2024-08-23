import { toast } from 'sonner';

export const useNotify = () => {
  const error = (message: string) =>
    toast.error(message, {
      duration: Infinity,
      cancel: { label: 'x', onClick: () => toast.dismiss() },
    });
  const info = (message: string) => toast.info(message, { duration: 5000 });
  const dismiss = (id: string | number) => toast.dismiss(id);

  return { error, info, dismiss };
};
