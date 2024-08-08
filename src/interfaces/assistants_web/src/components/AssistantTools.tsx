'use client';

import React from 'react';

import { Agent, ManagedTool } from '@/cohere-client';
import { Button, Icon, Text } from '@/components/Shared';
import { ToggleCard } from '@/components/ToggleCard';
import { WelcomeGuideTooltip } from '@/components/WelcomeGuideTooltip';
import { useAvailableTools } from '@/hooks/tools';
import { useParamsStore } from '@/stores';
import { cn } from '@/utils';
import { getToolIcon } from '@/utils/tools';

/**
 * @description Tools for the assistant to use in the conversation.
 */
export const AssistantTools: React.FC<{
  tools: ManagedTool[];
  agent?: Agent;
  className?: string;
}> = ({ tools, agent, className = '' }) => {
  const requiredTools = agent?.tools;
  const {
    params: { tools: paramTools },
  } = useParamsStore();
  const enabledTools = paramTools ?? [];
  const { availableTools, unauthedTools, handleToggle } = useAvailableTools({
    agent,
    managedTools: tools,
  });

  if (availableTools.length === 0) return null;

  return (
    <section className={cn('relative flex flex-col gap-y-5', className)}>
      <article className={cn('flex flex-col gap-y-5')}>
        {unauthedTools.length > 0 && <ConnectDataBox />}
        {unauthedTools.length > 0 && availableTools.length > 0 && (
          <hr className="border-t border-marble-950 dark:border-volcanic-300" />
        )}

        {availableTools.length > 0 && (
          <div className="flex flex-col gap-y-3">
            {availableTools.map(({ name, display_name, description, error_message }) => {
              const enabledTool = enabledTools.find((enabledTool) => enabledTool.name === name);
              const checked = !!enabledTool;
              const disabled = !!requiredTools;

              return (
                <ToggleCard
                  key={name}
                  disabled={disabled}
                  errorMessage={error_message}
                  checked={checked}
                  label={display_name ?? name ?? ''}
                  icon={getToolIcon(name)}
                  description={description ?? ''}
                  onToggle={(checked) => handleToggle(name ?? '', checked)}
                  agentId={agent?.id}
                />
              );
            })}
          </div>
        )}
      </article>
      <WelcomeGuideTooltip step={2} className="fixed right-0 mr-3 mt-12 md:right-full md:mt-0" />
    </section>
  );
};

/**
 * @description Info box that prompts the user to connect their data to enable tools
 */
const ConnectDataBox: React.FC = () => {
  return (
    <div className="flex flex-col gap-y-2">
      <div className="flex items-center justify-between">
        <Text as="span" styleAs="label" className="font-medium">
          Action Required
        </Text>
        <Icon name="warning" kind="outline" />
      </div>
      <div
        className={cn(
          'flex flex-col gap-y-4 rounded border border-coral-700 p-4 dark:border-evolved-green-500'
        )}
      >
        <div className="flex flex-col gap-y-3">
          <Text styleAs="h5">Connect your data</Text>
          <Text>
            In order to get the most accurate answers grounded on your data, connect the following:
          </Text>
          <Button href="/settings" icon="arrow-up-right">
            Connect data
          </Button>
        </div>
      </div>
    </div>
  );
};
