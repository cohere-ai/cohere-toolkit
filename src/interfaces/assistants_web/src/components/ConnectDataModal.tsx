'use client';

import { useRouter } from 'next/navigation';
import React from 'react';

import { Button, Text } from '@/components/Shared';

type Props = {
  onClose: VoidFunction;
};

/**
 * @description Modal that prompts the user to connect their data to enable tools and opens the settings drawer
 */
export const ConnectDataModal: React.FC<Props> = ({ onClose }) => {
  const router = useRouter();

  const handleClose = () => {
    onClose();
  };

  const handleStartConnecting = () => {
    router.push('/settings');
    handleClose();
  };

  return (
    <div className="flex flex-col gap-y-20">
      <Text>
        Your data must be connected in order to use this assistant. Connecting to your data will
        allow you to use the assistant to its full potential.
      </Text>
      <div className="flex justify-between">
        <Button label="Cancel" kind="secondary" onClick={handleClose} />
        <Button
          label="Start connecting"
          kind="secondary"
          theme="evolved-green"
          onClick={handleStartConnecting}
        />
      </div>
    </div>
  );
};
