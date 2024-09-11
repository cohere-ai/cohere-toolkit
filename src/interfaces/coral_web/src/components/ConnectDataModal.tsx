'use client';

import React from 'react';

import { Button, Text } from '@/components/Shared';
import { STRINGS } from '@/constants/strings';
import { useSettingsStore } from '@/stores';

type Props = {
  onClose: VoidFunction;
};

/**
 * @description Modal that prompts the user to connect their data to enable tools and opens the settings drawer
 */
export const ConnectDataModal: React.FC<Props> = ({ onClose }) => {
  const { setSettings } = useSettingsStore();

  const handleClose = () => {
    onClose();
  };

  const handleStartConnecting = () => {
    setSettings({ isConfigDrawerOpen: true });
    handleClose();
  };

  return (
    <div className="flex flex-col gap-y-20">
      <Text>{STRINGS.connectDataDescription}</Text>
      <div className="flex justify-between">
        <Button kind="secondary" onClick={handleClose}>
          {STRINGS.cancel}
        </Button>
        <Button kind="green" onClick={handleStartConnecting} splitIcon="arrow-right">
          {STRINGS.startConnecting}
        </Button>
      </div>
    </div>
  );
};
