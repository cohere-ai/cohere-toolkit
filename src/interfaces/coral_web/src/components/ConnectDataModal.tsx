'use client';

import React from 'react';

import { Button, Text } from '@/components/Shared';
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
      <Text>
        Your data must be connected in order to use this assistant. Connecting to your data will
        allow you to use the assistant to its full potential.
      </Text>
      <div className="flex justify-between">
        <Button kind="secondary" onClick={handleClose}>
          Cancel
        </Button>
        <Button kind="green" onClick={handleStartConnecting} splitIcon="arrow-right">
          Start connecting
        </Button>
      </div>
    </div>
  );
};
