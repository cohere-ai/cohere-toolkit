'use client';

import { Transition } from '@headlessui/react';
import React from 'react';

import { BotAvatar } from '@/components/Avatar';
import { Text } from '@/components/Shared';
import { useAgent } from '@/hooks/agents';
import { BotState } from '@/types/message';
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
      className="flex flex-col items-center gap-y-4 p-4 md:max-w-[480px] lg:max-w-[720px]"
      enter="transition-all duration-300 ease-out delay-300"
      enterFrom="opacity-0"
      enterTo="opacity-100"
      leave="transition-opacity duration-200"
      leaveFrom="opacity-100"
      leaveTo="opacity-0"
      as="div"
    >
      <div
        className={cn(
          'flex h-7 w-7 items-center justify-center rounded md:h-9 md:w-9',
          isAgent && getCohereColor(agent.id),
          {
            'bg-mushroom-700': !isAgent,
          }
        )}
      >
        {!isAgent ? (
          <BotAvatar state={BotState.FULFILLED} style="secondary" />
        ) : (
          <Text className="uppercase text-white" styleAs="p-lg">
            {agent.name[0]}
          </Text>
        )}
      </div>

      <Text
        styleAs="p-lg"
        className={cn(
          'text-center text-mushroom-400 md:!text-h4',
          isAgent && getCohereColor(agent.id, { background: false })
        )}
      >
        {!isAgent ? 'Need help? Your wish is my command.' : agent.name}
      </Text>
      {isAgent && (
        <Text className="!text-p-md text-center text-volcanic-100 md:!text-p-lg">
          {agent.description}
        </Text>
      )}
    </Transition>
  );
};
