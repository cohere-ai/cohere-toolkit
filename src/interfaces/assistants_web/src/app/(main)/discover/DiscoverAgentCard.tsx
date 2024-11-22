'use client';

import Link from 'next/link';

import { AgentPublic } from '@/cohere-client';
import { DeleteAgent } from '@/components/Modals/DeleteAgent';
import { CoralLogo, KebabMenu, Text } from '@/components/UI';
import { useContextStore } from '@/context';
import { useBrandedColors, useSession } from '@/hooks';
import { checkIsDefaultAgent, cn } from '@/utils';

type Props = {
  agent?: AgentPublic;
};

/**
 * @description renders a card for an agent with the agent's name, description
 */
export const DiscoverAgentCard: React.FC<Props> = ({ agent }) => {
  const isDefaultAgent = checkIsDefaultAgent(agent);
  const { bg, contrastText, contrastFill } = useBrandedColors(agent?.id);
  const session = useSession();
  const isCreator = agent?.user_id === session.userId;
  const createdBy = isDefaultAgent ? 'COHERE' : isCreator ? 'YOU' : 'TEAM';

  const { open, close } = useContextStore();

  const handleOpenDeleteModal = () => {
    if (!agent) return;
    open({
      title: `Delete ${agent.name}`,
      content: <DeleteAgent name={agent.name} agentId={agent.id} onClose={close} />,
    });
  };

  return (
    <Link
      className="flex overflow-x-hidden rounded-lg border border-volcanic-800 bg-volcanic-950 p-4 transition-colors duration-300 hover:bg-marble-950 dark:border-volcanic-300 dark:bg-volcanic-150 dark:hover:bg-volcanic-100"
      href={isDefaultAgent ? '/' : `/a/${agent?.id}`}
    >
      <div className="flex h-full flex-grow flex-col items-start gap-y-2 overflow-x-hidden">
        <div className="flex w-full items-center gap-x-2">
          <div
            className={cn(
              'relative flex h-8 w-8 flex-shrink-0 items-center justify-center rounded duration-300',
              bg
            )}
          >
            {isDefaultAgent ? (
              <CoralLogo className={contrastFill} />
            ) : (
              <Text className={cn('uppercase', contrastText)} styleAs="p-lg">
                {agent?.name[0]}
              </Text>
            )}
          </div>
          <Text as="h5" className="truncate dark:text-mushroom-950" title={agent?.name}>
            {agent?.name}
          </Text>
          {isCreator && (
            <div className="ml-auto">
              <KebabMenu
                anchor="right start"
                items={[
                  {
                    iconName: 'edit',
                    label: 'Edit assistant',
                    href: `/edit/${agent?.id}`,
                  },
                  {
                    iconName: 'trash',
                    label: 'Delete assistant',
                    iconClassName: 'fill-danger-500 dark:fill-danger-500',
                    onClick: handleOpenDeleteModal,
                  },
                ]}
              />
            </div>
          )}
        </div>
        <Text className="line-clamp-2 flex-grow dark:text-mushroom-800">{agent?.description}</Text>
        <Text className="dark:text-volcanic-500">BY {createdBy}</Text>
      </div>
    </Link>
  );
};
