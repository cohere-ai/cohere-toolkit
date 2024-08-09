'use client';

import { Logo } from '@/components/Shared';
import { env } from '@/env.mjs';
import { useSettingsStore } from '@/stores';

export const MobileHeader: React.FC = () => {
  const { setAgentsLeftSidePanelOpen, setAgentsRightSidePanelOpen } = useSettingsStore();
  const handleOpenLeftSidePanel = () => {
    setAgentsRightSidePanelOpen(false);
    setAgentsLeftSidePanelOpen(true);
  };

  return (
    <button onClick={handleOpenLeftSidePanel} className="flex h-full items-center gap-4 lg:hidden">
      <Logo hasCustomLogo={env.NEXT_PUBLIC_HAS_CUSTOM_LOGO} includeBrandName={false} />
    </button>
  );
};
