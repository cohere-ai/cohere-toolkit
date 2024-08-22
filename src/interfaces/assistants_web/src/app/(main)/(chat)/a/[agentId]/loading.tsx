import { Spinner } from '@/components/UI';

const Loading: React.FC<React.PropsWithChildren> = () => {
  return (
    <div className="flex h-screen w-full items-center justify-center bg-marble-980 dark:bg-volcanic-150">
      <Spinner className="h-10 w-10" />
    </div>
  );
};

export default Loading;
