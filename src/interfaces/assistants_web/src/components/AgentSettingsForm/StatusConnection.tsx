import { Text } from '@/components/UI';
import { cn } from '@/utils';

export const StatusConnection: React.FC<{ connected: boolean }> = ({ connected }) => {
  const label = connected ? 'Connected' : 'Disconnected';
  return (
    <Text styleAs="p-sm" className="flex items-center gap-2 uppercase dark:text-mushroom-950">
      <span
        className={cn('size-[10px] rounded-full', {
          'bg-evolved-green-700': connected,
          'bg-danger-500': !connected,
        })}
      />
      {label}
    </Text>
  );
};
