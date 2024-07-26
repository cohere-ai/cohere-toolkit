'use client';

import { Transition } from '@headlessui/react';
import React from 'react';

import { CoralLogo, Text } from '@/components/Shared';
import { useAgent } from '@/hooks/agents';
import { cn } from '@/utils';
import { getCohereColor } from '@/utils/getCohereColor';

type Props = {
  show: boolean;
  agentId?: string;
};

/**
 * @description Welcome message shown to the user when they first open the chat.
 */
export const Welcome: React.FC<Props> = ({ show, agentId }) => {
  const { data: agent, isLoading } = useAgent({ agentId });
  const isAgent = agentId !== undefined && !isLoading && !!agent;

  return (
    <Transition
      show={show}
      appear
      enter="transition-all duration-300 ease-out delay-300"
      enterFrom="opacity-0"
      enterTo="opacity-100"
      leave="transition-opacity duration-200"
      leaveFrom="opacity-100"
      leaveTo="opacity-0"
      as="div"
    >
      <div className="flex flex-col items-center gap-y-4 p-4 md:w-[380px] lg:w-[520px]">
        <div className="flex w-full items-center gap-x-3">
          <div
            className={cn(
              'flex h-7 w-7 items-center justify-center rounded md:h-9 md:w-9',
              getCohereColor(agent?.id, { background: true, contrastText: true })
            )}
          >
            {!isAgent ? (
              <CoralLogo />
            ) : (
              <Text className="uppercase" styleAs="p-lg">
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

        <Text styleAs="p-lg" className={cn('text-center md:!text-h4')}>
          {!isAgent ? 'Need help? Your wish is my command.' : agent.name}
        </Text>
        {isAgent && (
          <Text className="!text-p-md text-center text-volcanic-100 md:!text-p-lg">
            {agent.description}
          </Text>
        )}
      </div>
    </Transition>
  );
};
