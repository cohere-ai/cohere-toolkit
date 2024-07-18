'use client';

import { IconButton } from '@/components/IconButton';
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
    <header className="flex h-11 w-full items-center justify-between rounded-lg border border-marble-950 bg-marble-980 pl-5 pr-3 lg:hidden">
      <Logo />
      <IconButton iconName="menu" onClick={onToggleAgentsSidePanel} />
    </header>
  );
};
