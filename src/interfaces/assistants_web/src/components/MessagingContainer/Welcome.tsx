'use client';

import { Transition } from '@headlessui/react';
import React from 'react';

import { AssistantTools } from '@/components/MessagingContainer';
import { CoralLogo, Icon, Text } from '@/components/UI';
import { useAvailableTools } from '@/hooks';
import { useAgent, useBrandedColors, useListTools } from '@/hooks';
import { checkIsDefaultAgent } from '@/utils';
import { cn } from '@/utils';

type Props = {
  show: boolean;
  agentId?: string;
};

/**
 * @description Welcome message shown to the user when they first open the chat.
 */
export const Welcome: React.FC<Props> = ({ show, agentId }) => {
  const { data: agent, isLoading: isAgentsLoading } = useAgent({ agentId });
  const { data: tools = [], isLoading: isToolsLoading } = useListTools();
  const { contrastText, bg, contrastFill } = useBrandedColors(agentId);

  const isDefaultAgent = checkIsDefaultAgent(agent);

  const { availableTools } = useAvailableTools({
    agent,
    allTools: tools,
  });

  let toolToggleMessage = 'Toggle Tools On/Off';
  if (availableTools.length === 0) {
    toolToggleMessage = 'Your Agent has no Tools enabled. Update your Agent to add Tools.';
  }

  return (
    <Transition
      show={show && !isToolsLoading && !isAgentsLoading}
      enter="transition-all duration-300 ease-out delay-300"
      enterFrom="opacity-0"
      enterTo="opacity-100"
      leave="transition-opacity duration-200"
      leaveFrom="opacity-100"
      leaveTo="opacity-0"
      as="div"
    >
      <div className="flex flex-col gap-y-4 p-4 md:w-[380px] lg:w-[520px]">
        <div className="flex w-full items-center gap-x-3">
          <div
            className={cn(
              'flex h-7 w-7 items-center justify-center rounded md:h-9 md:w-9',
              contrastText,
              bg
            )}
          >
            {isDefaultAgent ? (
              <CoralLogo className={contrastFill} />
            ) : (
              <Text className={cn('uppercase', contrastText)} styleAs="p-lg">
                {agent?.name[0]}
              </Text>
            )}
          </div>
          <Text styleAs="h4" className="truncate">
            {isDefaultAgent ? 'Your Public Assistant' : agent?.name}
          </Text>
          {isDefaultAgent && (
            <Text className="ml-auto" styleAs="caption">
              By Cohere
            </Text>
          )}
        </div>
        <Text className="text-mushroom-300 dark:text-marble-800">
          {agent?.description || 'Ask questions and get answers based on your tools and files.'}
        </Text>

        <div className="flex items-center gap-x-1">
          <Icon name="circles-four" kind="outline" />
          <Text className="font-medium">{toolToggleMessage}</Text>
        </div>

        <AssistantTools agent={agent} tools={tools} />
      </div>
    </Transition>
  );
};
