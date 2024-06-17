import { Transition } from '@headlessui/react';
import Link from 'next/link';

import { CoralLogo, Text, Tooltip } from '@/components/Shared';
import { useSettingsStore } from '@/stores';
import { cn } from '@/utils';
import { getCohereColor } from '@/utils/getCohereColor';

/**
 * @description
 */
export const LeftPanel: React.FC = () => {
  const {
    settings: { isAgentsSidePanelOpen },
  } = useSettingsStore();

  return (
    <div className="flex flex-col gap-3">
      {isAgentsSidePanelOpen && (
        <Text styleAs="label" className="text-green-800">
          Most recent
        </Text>
      )}
      <AgentCard isExpanded={isAgentsSidePanelOpen} name="Command R+" isBaseAgent />
      <AgentCard
        isExpanded={isAgentsSidePanelOpen}
        name="HR Policy Advisor"
        id="hr-policy-advisor-01"
      />
    </div>
  );
};

type AgentCardProps = {
  isExpanded: boolean;
  name: string;
  isBaseAgent?: boolean;
  id?: string;
};

const AgentCard: React.FC<AgentCardProps> = ({ name, id, isBaseAgent, isExpanded }) => {
  return (
    <Tooltip label={name} placement="right" hover={!isExpanded}>
      <Link
        href={isBaseAgent ? '/agents' : `/agents?id=${id}`}
        className="flex w-full items-center gap-x-2 rounded-lg p-2 transition-colors hover:bg-marble-300"
        shallow
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
          className="overflow-x-hidden"
          enter="transition-opacity duration-100 ease-in-out delay-300 duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
        >
          <Text className="truncate">{name}</Text>
        </Transition>
      </Link>
    </Tooltip>
  );
};
