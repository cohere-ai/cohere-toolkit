import { Transition } from '@headlessui/react';

import { AgentCard } from '@/components/Agents/AgentCard';
import { Text } from '@/components/Shared';
import { useSettingsStore } from '@/stores';

/**
 * @description This component renders a list of agents.
 * It shows the most recent agents and the base agents.
 */
export const AgentsList: React.FC = () => {
  const {
    settings: { isAgentsSidePanelOpen },
  } = useSettingsStore();

  return (
    <div className="flex flex-col gap-3">
      <Transition
        as="div"
        show={isAgentsSidePanelOpen}
        enter="transition-all ease-in-out delay-300 duration-300"
        enterFrom="opacity-0"
        enterTo="opacity-100"
      >
        <Text styleAs="label" className="text-green-800">
          Most recent
        </Text>
      </Transition>

      <AgentCard isExpanded={isAgentsSidePanelOpen} name="Command R+" isBaseAgent />
      <AgentCard
        isExpanded={isAgentsSidePanelOpen}
        name="HR Policy Advisor"
        id="hr-policy-advisor-01"
      />
      <AgentCard
        isExpanded={isAgentsSidePanelOpen}
        name="Financial Advisor"
        id="financial-advisor-01"
      />
    </div>
  );
};
