'use client';

import { ShareModal } from '@/components/ShareModal';
import { Button, Text } from '@/components/Shared';
import { useContextStore } from '@/context';
import { useAgent } from '@/hooks/agents';
import { useConversationStore } from '@/stores';
import { cn } from '@/utils';
import { getCohereColor } from '@/utils/getCohereColor';

type Props = {
  agentId?: string;
};

export const Header: React.FC<Props> = ({ agentId }) => {
  const {
    conversation: { id },
  } = useConversationStore();

  const { data: agent, isLoading } = useAgent({ agentId });
  const { open } = useContextStore();
  const accentColor = getCohereColor(agentId, { text: true });

  const handleOpenShareModal = () => {
    if (!id) return;
    open({
      title: 'Share link to conversation',
      content: <ShareModal conversationId={id} />,
    });
  };

  return (
    <div className="flex h-header w-full min-w-0 items-center">
      <div className="flex w-full flex-1 items-center justify-between px-10">
        <div className="flex items-center gap-4">
          <Text className="truncate dark:text-mushroom-950" styleAs="p-lg" as="span">
            {isLoading ? '' : agent?.name ?? 'Cohere AI'}
          </Text>
          {agentId && (
            <Text
              styleAs="label-sm"
              className={cn(
                'rounded bg-volcanic-200 px-2 py-1 uppercase dark:text-mushroom-950',
                getCohereColor(agentId, { contrastText: true, background: true })
              )}
            >
              Private
            </Text>
          )}
        </div>
        {id && (
          <Button
            kind="secondary"
            className={cn('hidden md:flex', accentColor)}
            label={<Text className={accentColor}>Share</Text>}
            icon="share"
            iconOptions={{
              kind: 'outline',
              className: 'dark:group-hover:text-inherit dark:text-inherit',
            }}
            iconPosition="start"
            onClick={handleOpenShareModal}
          />
        )}
      </div>
    </div>
  );
};
