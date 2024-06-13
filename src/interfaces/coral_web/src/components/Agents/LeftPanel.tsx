import { AddAgentButton } from '@/components/Agents/AddAgentButton';
import { BaseAgentButton } from '@/components/Agents/BaseAgentButton';
import { useListAgents } from '@/hooks/agents';

import { CustomAgentButton } from './CustomAgentButton';

/**
 * @description renders the left panel containing the base agent, a list of agents, and an add agent button.
 */
export const LeftPanel: React.FC = () => {
  const { data: agents } = useListAgents();

  return (
    <div className="flex flex-col gap-3">
      <BaseAgentButton />
      {agents?.map((agent) => (
        <CustomAgentButton key={agent.id} id={agent.id} name={agent.name} />
      ))}
      <AddAgentButton />
    </div>
  );
};
