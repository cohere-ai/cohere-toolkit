import React from 'react';

import { Button, Icon, Text } from '@/components/Shared';

/**
 * @description Additional section in the tools settings tab for agents that prompts
 * the user to connect their data to enable tools
 */
export const AgentToolsTabSection = () => {
  const isDataConnectionRequired = true;
  return (
    <div className="flex flex-col gap-y-5">
      <Text styleAs="p-sm" className="text-secondary-800">
        Tools are data sources the assistant can search such as databases or the internet.
      </Text>
      {isDataConnectionRequired && (
        <div className="flex flex-col">
          <div className="flex items-center justify-between">
            <Text styleAs="label" className="font-medium">
              action required
            </Text>
            <Icon name="warning" />
          </div>
          <InfoBox />
        </div>
      )}
    </div>
  );
};

/**
 *
 * @description Info box that prompts the user to connect their data to enable tools
 */
const InfoBox = () => {
  return (
    <div className="bg-coral-200 border-coral-400 flex flex-col gap-y-4 rounded border-2 border-dashed p-4">
      <div className="flex flex-col gap-y-3">
        <Text>Connect your data</Text>
        <Text>
          In order to get the most accurate answered grounded on your data, experience, connect the
          following:
        </Text>
      </div>
      <Button kind="secondary" href={''} target="_blank">
        Google Drive
      </Button>
    </div>
  );
};
