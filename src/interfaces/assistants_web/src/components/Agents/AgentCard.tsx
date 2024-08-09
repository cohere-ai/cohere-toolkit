'use client';

import { usePathname, useRouter } from 'next/navigation';

import { CoralLogo, Text, Tooltip } from '@/components/Shared';
import { useBrandedColors } from '@/hooks/brandedColors';
import { useChatRoutes } from '@/hooks/chatRoutes';
import { useFileActions } from '@/hooks/files';
import {
  useCitationsStore,
  useConversationStore,
  useParamsStore,
  useSettingsStore,
} from '@/stores';
import { cn } from '@/utils';

type Props = {
  name: string;
  isBaseAgent?: boolean;
  id?: string;
};

/**
 * @description This component renders an agent card.
 * It shows the agent's name and a colored icon with the first letter of the agent's name.
 * If the agent is a base agent, it shows the Coral logo instead.
 */
export const AgentCard: React.FC<Props> = ({ name, id, isBaseAgent }) => {
  const { conversationId } = useChatRoutes();
  const router = useRouter();
  const pathname = usePathname();
  const { setAgentsLeftSidePanelOpen } = useSettingsStore();

  const isActive = isBaseAgent
    ? conversationId
      ? pathname === `/c/${conversationId}`
      : pathname === '/'
    : conversationId
    ? pathname === `/a/${id}/c/${conversationId}`
    : pathname === `/a/${id}`;

  const { bg, contrastText, contrastFill } = useBrandedColors(id);

  const { resetConversation } = useConversationStore();
  const { resetCitations } = useCitationsStore();
  const { resetFileParams } = useParamsStore();
  const { clearComposerFiles } = useFileActions();

  const resetConversationSettings = () => {
    clearComposerFiles();
    resetConversation();
    resetCitations();
    resetFileParams();
  };

  const handleClick = () => {
    if (isActive) return;

    const url = isBaseAgent ? '/' : `/a/${id}`;

    router.push(url);

    resetConversationSettings();
    setAgentsLeftSidePanelOpen(false);
  };

  return (
    <Tooltip label={name} placement="bottom" hover size="sm">
      <div
        onClick={handleClick}
        className={cn(
          'group flex w-full items-center justify-between gap-x-2 rounded-lg p-2 transition-colors hover:cursor-pointer hover:bg-mushroom-800 dark:hover:bg-volcanic-200',
          {
            'bg-mushroom-800 dark:bg-volcanic-200': isActive,
          }
        )}
      >
        <div
          className={cn(
            'flex size-8 flex-shrink-0 items-center justify-center rounded duration-300',
            bg
          )}
        >
          {isBaseAgent && <CoralLogo className={contrastFill} />}
          {!isBaseAgent && (
            <Text className={cn('uppercase', contrastText)} styleAs="p-lg">
              {name[0]}
            </Text>
          )}
        </div>
      </div>
    </Tooltip>
  );
};
