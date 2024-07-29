'use client';

import { IconButton } from '@/components/IconButton';
import { Button, Logo } from '@/components/Shared';
import { useAgentsStore } from '@/stores';

export const MobileHeader: React.FC = () => {
  const {
    setAgentsRightSidePanelOpen,
    agents: { isAgentsRightPanelOpen },
  } = useAgentsStore();

  const open = () => {
    setAgentsRightSidePanelOpen(true);
  };

  const close = () => {
    setAgentsRightSidePanelOpen(false);
  };

  return (
    <header className="flex h-11 w-full items-center justify-between pl-5 pr-3 lg:hidden">
      {isAgentsRightPanelOpen ? (
        <Button onClick={close} label="Knowledge" icon="close-drawer" kind="secondary" />
      ) : (
        <>
          <Logo />
          <IconButton iconName="menu" onClick={open} />
        </>
      )}
    </header>
  );
};
