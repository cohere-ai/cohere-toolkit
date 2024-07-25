'use client';

import { Button, CoralLogo, Text } from '@/components/Shared';
import { cn } from '@/utils';
import { getCohereColor } from '@/utils/getCohereColor';

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
  return (
    <article className="flex overflow-x-hidden rounded-lg border border-marble-950 bg-marble-980 p-4 dark:border-volcanic-300 dark:bg-volcanic-150">
      <div className="flex h-full flex-grow flex-col items-start gap-y-2 overflow-x-hidden">
        <div className="flex w-full items-center gap-x-2">
          <div
            className={cn(
              'flex h-8 w-8 flex-shrink-0 items-center justify-center rounded duration-300',
              'truncate',
              id && getCohereColor(id),
              {
                'bg-mushroom-700': isBaseAgent,
              }
            )}
          >
            {isBaseAgent ? (
              <CoralLogo style="secondary" />
            ) : (
              <Text className="uppercase text-white" styleAs="p-lg">
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
            className="dark:[&_span]:text-evolved-green-700"
            label="Try now"
            kind="secondary"
            endIcon="arrow-up-right"
          />
          {!isBaseAgent && (
            <Button
              href={`/edit/${id}`}
              className="dark:[&_span]:text-evolved-green-700"
              label="Edit"
              kind="secondary"
              endIcon="edit"
            />
          )}
        </div>
      </div>
    </article>
  );
};
