import AddAgentButton from '@/components/Agents/AddAgentButton';
import BaseAgentButton from '@/components/Agents/BaseAgentButton';

const LeftPanel: React.FC = () => {
  return (
    <div className="flex flex-col gap-3">
      <BaseAgentButton />
      <AddAgentButton />
    </div>
  );
};

export default LeftPanel;
