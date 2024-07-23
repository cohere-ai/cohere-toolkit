import { Text } from '@/components/Shared';
import { cn } from '@/utils';

type Props = {
  sequence: string[];
  className?: string;
};

export const Shortcut: React.FC<Props> = ({ sequence, className }) => {
  return (
    <section className={cn('rounded-md bg-volcanic-300 px-1.5 dark:bg-volcanic-300', className)}>
      <Text as="kbd" className="text-white">
        {sequence.join(' + ')}
      </Text>
    </section>
  );
};
