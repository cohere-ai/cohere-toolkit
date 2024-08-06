'use client';

import React from 'react';

import { Agent, ManagedTool } from '@/cohere-client';
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
  const { availableTools, handleToggle } = useAvailableTools({
    agent,
    managedTools: tools,
  });

  if (availableTools.length === 0) return null;

  return (
    <section className={cn('relative flex flex-col gap-y-5', className)}>
      {availableTools.length > 0 && (
        <div className="flex flex-col gap-y-3">
          {availableTools.map(({ name, display_name, description, error_message }) => {
            const enabledTool = enabledTools.find((enabledTool) => enabledTool.name === name);
            const checked = !!enabledTool;
            const disabled = !!requiredTools && agent.id !== DEFAULT_ASSISTANT_ID;

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
      <WelcomeGuideTooltip step={2} className="fixed right-0 mr-3 mt-12 md:right-full md:mt-0" />
    </section>
  );
};
