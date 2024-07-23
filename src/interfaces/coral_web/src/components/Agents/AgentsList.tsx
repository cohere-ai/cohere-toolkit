'use client';

import { Transition } from '@headlessui/react';

import { AgentCard } from '@/components/Agents/AgentCard';
import { Text } from '@/components/Shared';
import { useRecentAgents } from '@/hooks/agents';
import { useAgentsStore } from '@/stores';

/**
 * @description This component renders a list of agents.
 * It shows the most recent agents and the base agents.
 */
export const AgentsList: React.FC = () => {
  const {
    agents: { isAgentsSidePanelOpen },
  } = useAgentsStore();
  const { recentAgents } = useRecentAgents();
  return (
    <div className="flex flex-col gap-3">
      <Transition
        as="div"
        show={isAgentsSidePanelOpen}
        enter="transition-all ease-in-out delay-300 duration-300"
        enterFrom="opacity-0"
        enterTo="opacity-100"
      >
        <Text styleAs="label" className="truncate text-green-200">
          Your assistants
        </Text>
      </Transition>

      <AgentCard isExpanded={isAgentsSidePanelOpen} name="Command R+" isBaseAgent />
      {recentAgents.map((agent) => (
        <AgentCard
          key={agent.id}
          isExpanded={isAgentsSidePanelOpen}
          name={agent.name}
          id={agent.id}
        />
      ))}
    </div>
  );
};
