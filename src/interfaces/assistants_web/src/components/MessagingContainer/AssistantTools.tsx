'use client';

import React from 'react';

import { AgentPublic, ManagedTool } from '@/cohere-client';
import { WelcomeGuideTooltip } from '@/components/MessagingContainer';
import { Button, Icon, Text, Tooltip } from '@/components/UI';
import { useAvailableTools, useBrandedColors } from '@/hooks';
import { cn, getToolIcon } from '@/utils';

/**
 * @description Tools for the assistant to use in the conversation.
 */
export const AssistantTools: React.FC<{
  tools: ManagedTool[];
  agent?: AgentPublic;
  className?: string;
}> = ({ tools, agent, className = '' }) => {
  const { knowledgeTools, unauthedTools } = useAvailableTools({
    agent,
    managedTools: tools,
  });

  if (knowledgeTools.length === 0) return null;

  return (
    <section className={cn('relative flex flex-col gap-y-5', className)}>
      <article className={cn('flex flex-col gap-y-5')}>
        {knowledgeTools.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {knowledgeTools.map(({ name, display_name, is_auth_required }) => {
              return (
                <div key={name} className="relative">
                  <Tooltip hover label={display_name} size="sm">
                    <div className="flex justify-center rounded bg-mushroom-900 p-1 dark:bg-volcanic-150">
                      <button
                        onClick={() => console.log(name)}
                        className="flex items-center gap-2.5 px-2 py-1"
                      >
                        <Icon name={getToolIcon(name)} size="md" />
                        <Text className={cn({ hidden: knowledgeTools.length > 6 })}>
                          {display_name}
                        </Text>
                      </button>
                    </div>
                    <div
                      className={cn(
                        'absolute -bottom-[2px] -right-[1.5px] size-1.5 rounded-full bg-volcanic-600',
                        {
                          'bg-success-300': !is_auth_required,
                        }
                      )}
                    />
                  </Tooltip>
                </div>
              );
            })}
          </div>
        )}
        {unauthedTools.length > 0 && <ConnectDataBox agentId={agent?.id} />}
      </article>
      <WelcomeGuideTooltip step={2} className="fixed right-0 mr-3 mt-12 md:right-full md:mt-0" />
    </section>
  );
};

/**
 * @description Info box that prompts the user to connect their data to enable tools
 */
const ConnectDataBox: React.FC<{ agentId?: string }> = ({ agentId }) => {
  const { text, lightText, dark, light } = useBrandedColors(agentId);
  return (
    <div
      className={cn(
        'flex flex-col gap-y-4 rounded border border-marble-900 bg-marble-950 p-4 dark:border-volcanic-300 dark:bg-volcanic-150'
      )}
    >
      <div className="flex flex-col gap-y-3">
        <header className="flex items-center gap-2">
          <Icon name="information" kind="outline" />
          <Text styleAs="label" className="font-medium">
            connect knowledge sources
          </Text>
        </header>
        <Text>Your assistant needs connections in order to use its knowledge sources,</Text>
        <Button kind="secondary" theme="coral" className="ml-auto uppercase" href="/settings">
          <Text styleAs="label" className={cn('font-medium', dark(lightText), light(text))}>
            Manage
          </Text>
        </Button>
      </div>
    </div>
  );
};
