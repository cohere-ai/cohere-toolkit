import { Spinner } from '@/components/Shared';

const Loading: React.FC<React.PropsWithChildren> = () => {
  return (
    <div className="flex h-screen w-full items-center justify-center bg-mushroom-950 dark:bg-volcanic-150">
      <Spinner className="h-10 w-10" />
    </div>
  );
};

export default Loading;
