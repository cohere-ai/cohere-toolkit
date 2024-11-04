'use client';

import { Transition } from '@headlessui/react';
import React from 'react';

import { AssistantTools } from '@/components/MessagingContainer';
import { CoralLogo, Icon, Text } from '@/components/UI';
import { BASE_AGENT_EXCLUDED_TOOLS } from '@/constants';
import { useAgent, useBrandedColors, useListTools } from '@/hooks';
import { cn } from '@/utils';
import { checkIsBaseAgent } from '@/utils';

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

  const isBaseAgent = checkIsBaseAgent(agent);
  // Filter out tools that are excluded for the base agent
  let toolsFiltered = [...tools];
  if (isBaseAgent) {
    toolsFiltered = tools.filter((tool) => !BASE_AGENT_EXCLUDED_TOOLS.includes(tool.name ?? ''));
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
            {isBaseAgent ? (
              <CoralLogo className={contrastFill} />
            ) : (
              <Text className={cn('uppercase', contrastText)} styleAs="p-lg">
                {agent?.name[0]}
              </Text>
            )}
          </div>
          <Text styleAs="h4" className="truncate">
            {isBaseAgent ? 'Your Public Assistant' : agent?.name}
          </Text>
          {isBaseAgent && (
            <Text className="ml-auto" styleAs="caption">
              By Cohere
            </Text>
          )}
        </div>
        <Text className="text-mushroom-300 dark:text-marble-800">
          {agent?.description || 'Ask questions and get answers based on your files.'}
        </Text>

        {isBaseAgent && (
          <div className="flex items-center gap-x-1">
            <Icon name="circles-four" kind="outline" />
            <Text className="font-medium">Toggle Tools On/Off</Text>
          </div>
        )}
        <AssistantTools agent={agent} tools={toolsFiltered} />
      </div>
    </Transition>
  );
};
