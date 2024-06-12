import { AddAgentButton } from '@/components/Agents/AddAgentButton';
import { BaseAgentButton } from '@/components/Agents/BaseAgentButton';

/**
 * @description renders the left panel containing the base agent, a list of agents, and an add agent button.
 */
export const LeftPanel: React.FC = () => {
  return (
    <div className="flex flex-col gap-3">
      <BaseAgentButton />
      <AddAgentButton />
    </div>
  );
};
