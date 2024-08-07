'use client';

import { ShareModal } from '@/components/ShareModal';
import { Button, Icon, Text } from '@/components/Shared';
import { useContextStore } from '@/context';
import { useAgent } from '@/hooks/agents';
import { useBrandedColors } from '@/hooks/brandedColors';
import { useConversationStore } from '@/stores';
import { cn } from '@/utils';

type Props = {
  agentId?: string;
};

export const Header: React.FC<Props> = ({ agentId }) => {
  const {
    conversation: { id },
  } = useConversationStore();

  const { data: agent, isLoading } = useAgent({ agentId });
  const { open } = useContextStore();
  const { text, fill, contrastText, bg } = useBrandedColors(agentId);

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
                contrastText,
                bg
              )}
            >
              Private
            </Text>
          )}
        </div>
        {id && (
          <Button
            kind="secondary"
            className={cn('hidden md:flex')}
            label={<Text className={text}>Share</Text>}
            iconOptions={{
              customIcon: <Icon name="share" kind="outline" className={fill} />,
            }}
            iconPosition="start"
            onClick={handleOpenShareModal}
          />
        )}
      </div>
    </div>
  );
};
