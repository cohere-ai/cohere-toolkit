import { Transition } from '@headlessui/react';
import { useRouter } from 'next/router';

import { KebabMenu } from '@/components/KebabMenu';
import { CoralLogo, Text, Tooltip } from '@/components/Shared';
import { useRecentAgents } from '@/hooks/agents';
import { getIsTouchDevice } from '@/hooks/breakpoint';
import { useSlugRoutes } from '@/hooks/slugRoutes';
import { useAgentsStore, useCitationsStore, useConversationStore, useParamsStore } from '@/stores';
import { cn } from '@/utils';
import { getCohereColor } from '@/utils/getCohereColor';

type Props = {
  isExpanded: boolean;
  name: string;
  isBaseAgent?: boolean;
  id?: string;
};

/**
 * @description This component renders an agent card.
 * It shows the agent's name and a colored icon with the first letter of the agent's name.
 * If the agent is a base agent, it shows the Coral logo instead.
 */
export const AgentCard: React.FC<Props> = ({ name, id, isBaseAgent, isExpanded }) => {
  const isTouchDevice = getIsTouchDevice();
  const { agentId } = useSlugRoutes();
  const isActive = isBaseAgent ? !agentId : agentId === id;
  const router = useRouter();

  const { removeRecentAgentId } = useRecentAgents();
  const { setEditAgentPanelOpen } = useAgentsStore();
  const { resetConversation } = useConversationStore();
  const { resetCitations } = useCitationsStore();
  const { resetFileParams } = useParamsStore();

  const handleNewChat = () => {
    const url = id ? `/agents/${id}` : '/agents';
    router.push(url, undefined, { shallow: true });
    setEditAgentPanelOpen(false);
    resetConversation();
    resetCitations();
    resetFileParams();
  };

  const handleHideAssistant = () => {
    if (id) removeRecentAgentId(id);
  };

  return (
    <Tooltip label={name} placement="right" hover={!isExpanded}>
      <div
        onClick={handleNewChat}
        className={cn(
          'group flex w-full items-center justify-between gap-x-2 rounded-lg p-2 transition-colors hover:cursor-pointer hover:bg-marble-300',
          {
            'bg-marble-300': isActive,
          }
        )}
      >
        <div
          className={cn(
            'flex h-8 w-8 flex-shrink-0 items-center justify-center rounded duration-300',
            id && getCohereColor(id),
            {
              'bg-secondary-400': isBaseAgent,
            }
          )}
        >
          {isBaseAgent && <CoralLogo style="secondary" />}
          {!isBaseAgent && (
            <Text className="uppercase text-white" styleAs="p-lg">
              {name[0]}
            </Text>
          )}
        </div>
        <Transition
          as="div"
          show={isExpanded}
          className="flex-grow overflow-x-hidden"
          enter="transition-opacity duration-100 ease-in-out delay-300 duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
        >
          <Text className="truncate">{name}</Text>
        </Transition>
        <Transition
          as="div"
          show={isExpanded && !isBaseAgent}
          enter="transition-opacity duration-100 ease-in-out delay-300 duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
        >
          <KebabMenu
            anchor="right start"
            className={cn('flex', {
              'hidden group-hover:flex': !isTouchDevice,
            })}
            items={[
              {
                label: 'New chat',
                onClick: handleNewChat,
                iconName: 'new-message',
              },
              {
                label: 'Hide assistant',
                onClick: handleHideAssistant,
                iconName: 'hide',
              },
            ]}
          />
        </Transition>
      </div>
    </Tooltip>
  );
};
