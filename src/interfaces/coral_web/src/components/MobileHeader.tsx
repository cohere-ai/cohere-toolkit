import { Logo } from '@/components/Shared';
import { useAgentsStore } from '@/stores';

export const MobileHeader: React.FC = () => {
  const {
    agents: { isAgentsSidePanelOpen },
    setAgentsSidePanelOpen,
  } = useAgentsStore();

  const onToggleAgentsSidePanel = () => {
    setAgentsSidePanelOpen(!isAgentsSidePanelOpen);
  };

  return (
    <header className="flex h-11 items-center justify-start rounded-lg border border-marble-400 bg-marble-200 px-4 lg:hidden">
      <button onClick={onToggleAgentsSidePanel}>
        <Logo />
      </button>
    </header>
  );
};
