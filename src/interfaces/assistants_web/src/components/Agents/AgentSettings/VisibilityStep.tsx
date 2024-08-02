import { Icon, RadioGroup, Text } from '@/components/Shared';
import { cn } from '@/utils';

type Props = {
  isPublic: boolean;
  setIsPublic: (isPublic: boolean) => void;
};

export const VisibilityStep: React.FC<Props> = ({ isPublic, setIsPublic }) => {
  return (
    <div className="flex flex-col space-y-4">
      <RadioGroup
        value={isPublic ? 'public' : 'private'}
        options={[
          {
            value: 'public',
            label: 'Company (Everyone in your organization can access)',
          },
          // { value: 'private', label: 'Private (Only you can access)' },
        ]}
        onChange={(val) => setIsPublic(val === 'public')}
      />
      <div
        className={cn(
          'flex space-x-2 rounded-lg border border-dashed p-4 dark:border-volcanic-500 dark:bg-volcanic-300',
          { hidden: !isPublic }
        )}
      >
        <Icon
          name="warning"
          kind="outline"
          className="mx-1 fill-danger-500 dark:fill-danger-500"
          size="lg"
        />
        <Text>
          All files will be public, including any private files you add from your Drive or local.
          Those will be viewable/accessible to everyone.
        </Text>
      </div>
    </div>
  );
};
