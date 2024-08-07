'use client';

import { Transition } from '@headlessui/react';
import React from 'react';

import { AssistantTools } from '@/components/AssistantTools';
import { CoralLogo, Icon, Text } from '@/components/Shared';
import { useAgent } from '@/hooks/agents';
import { useBrandedColors } from '@/hooks/brandedColors';
import { useListTools } from '@/hooks/tools';
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

  const isAgent = agentId !== undefined && !isAgentsLoading && !!agent;

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
            {!isAgent ? (
              <CoralLogo className={contrastFill} />
            ) : (
              <Text className={cn('uppercase', contrastText)} styleAs="p-lg">
                {agent.name[0]}
              </Text>
            )}
          </div>
          <Text styleAs="h4" className="truncate">
            {isAgent ? agent.name : 'Your Private Assistant'}
          </Text>
          {!isAgent && (
            <Text className="ml-auto" styleAs="caption">
              By Cohere
            </Text>
          )}
        </div>
        <Text className="text-mushroom-300 dark:text-marble-800">
          {agent?.description || 'Ask questions and get answers based on your files.'}
        </Text>

        {!isAgent && (
          <div className="flex items-center gap-x-1">
            <Icon name="circles-four" kind="outline" />
            <Text className="font-medium">Toggle Tools On/Off</Text>
          </div>
        )}
        <AssistantTools agent={agent} tools={tools} />
      </div>
    </Transition>
  );
};
