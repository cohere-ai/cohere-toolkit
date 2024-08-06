'use client';

import { Button, CoralLogo, Text } from '@/components/Shared';
import { useBrandedColors } from '@/hooks/brandedColors';
import { cn } from '@/utils';

type Props = {
  name: string;
  description?: string;
  isBaseAgent?: boolean;
  id?: string;
};

/**
 * @description renders a card for an agent with the agent's name, description
 */
export const DiscoverAgentCard: React.FC<Props> = ({ id, name, description, isBaseAgent }) => {
  const { bg, contrastText } = useBrandedColors(id);

  return (
    <article className="flex overflow-x-hidden rounded-lg border border-volcanic-800 bg-volcanic-950 p-4 dark:border-volcanic-300 dark:bg-volcanic-150">
      <div className="flex h-full flex-grow flex-col items-start gap-y-2 overflow-x-hidden">
        <div className="flex w-full items-center gap-x-2">
          <div
            className={cn(
              'flex h-8 w-8 flex-shrink-0 items-center justify-center rounded duration-300',
              'truncate',
              bg
            )}
          >
            {isBaseAgent ? (
              <CoralLogo />
            ) : (
              <Text className={cn('uppercase text-white', contrastText)} styleAs="p-lg">
                {name[0]}
              </Text>
            )}
          </div>
          <Text as="h5" className="truncate dark:text-mushroom-950">
            {name}
          </Text>
        </div>
        <Text className="line-clamp-2 flex-grow dark:text-mushroom-800">{description}</Text>
        <Text className="dark:text-volcanic-500">BY {isBaseAgent ? 'COHERE' : 'YOU'}</Text>
        <div className="flex w-full items-center justify-between">
          <Button
            href={isBaseAgent ? '/' : `/a/${id}`}
            label="Try now"
            kind="secondary"
            icon="arrow-up-right"
            iconPosition="end"
            theme="evolved-green"
          />
          {!isBaseAgent && (
            <Button
              href={`/edit/${id}`}
              label="Edit"
              kind="secondary"
              icon="edit"
              iconPosition="end"
              theme="evolved-green"
            />
          )}
        </div>
      </div>
    </article>
  );
};
