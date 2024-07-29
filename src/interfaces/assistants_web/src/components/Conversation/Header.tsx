'use client';

import { ShareModal } from '@/components/ShareModal';
import { Button, Icon, Text } from '@/components/Shared';
import { useContextStore } from '@/context';
import { useConversationStore } from '@/stores';
import { cn } from '@/utils';
import { getCohereColor } from '@/utils/getCohereColor';

type Props = {
  agentId?: string;
};

export const Header: React.FC<Props> = ({ agentId }) => {
  const {
    conversation: { id, name },
  } = useConversationStore();
  const { open } = useContextStore();
  const accentColor = getCohereColor(agentId, { background: false, text: true });

  const handleOpenShareModal = () => {
    if (!id) return;
    open({
      title: 'Share link to conversation',
      content: <ShareModal conversationId={id} />,
    });
  };

  return (
    <div className="flex h-header w-full min-w-0 items-center border-b border-marble-950 dark:border-b-0">
      <div className="flex w-full flex-1 items-center justify-between px-10">
        <div className="flex items-center gap-4">
          <Text className="truncate dark:text-mushroom-950" styleAs="p-lg" as="span">
            {name}
          </Text>
          {agentId && (
            <Text
              styleAs="label-sm"
              className={cn(
                'rounded bg-volcanic-200 px-2 py-1 uppercase dark:text-mushroom-950',
                accentColor
              )}
            >
              Private
            </Text>
          )}
        </div>
        {id && (
          <Button
            kind="secondary"
            className="hidden md:flex"
            label={<Text className={cn('dark:text-mushroom-950', accentColor)}>Share</Text>}
            icon="share"
            iconOptions={{ kind: 'outline', className: cn('dark:fill-mushroom-950', accentColor) }}
            onClick={handleOpenShareModal}
          />
        )}
      </div>
    </div>
  );
};
