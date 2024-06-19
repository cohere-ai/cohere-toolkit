import { Transition } from '@headlessui/react';
import React from 'react';

import { BotAvatar } from '@/components/Avatar';
import { Text } from '@/components/Shared';
import { BotState } from '@/types/message';
import { cn } from '@/utils';
import { getCohereColor } from '@/utils/getCohereColor';

type BaseAgentProps = {
  show: boolean;
  isBaseAgent: true;
};

type AgentProps = {
  show: boolean;
  isBaseAgent?: false;
  id: string;
  name: string;
  description?: string;
};

type Props = BaseAgentProps | AgentProps;

const isBaseAgent = (props: AgentProps | BaseAgentProps): props is BaseAgentProps => {
  return Boolean(props.isBaseAgent);
};

/**
 * @description Welcome message shown to the user when they first open the chat.
 */
export const Welcome: React.FC<Props> = (props) => {
  const isBaseAgentProps = isBaseAgent(props);

  return (
    <Transition
      show={props.show}
      appear
      className="flex flex-col items-center gap-y-4"
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
          !isBaseAgentProps && getCohereColor(props.id),
          {
            'bg-secondary-400': isBaseAgentProps,
          }
        )}
      >
        {isBaseAgentProps ? (
          <BotAvatar state={BotState.FULFILLED} style="secondary" />
        ) : (
          <Text className="uppercase text-white" styleAs="p-lg">
            {props.name[0]}
          </Text>
        )}
      </div>

      <Text
        styleAs="p-lg"
        className={cn(
          'text-center text-secondary-800 md:!text-h4',
          !isBaseAgentProps && getCohereColor(props.id, { background: false })
        )}
      >
        {isBaseAgentProps ? 'Need help? Your wish is my command.' : props.name}
      </Text>
      {!isBaseAgentProps && (
        <Text className="!text-p-md text-center text-volcanic-900 md:!text-p-lg">
          {props.description}
        </Text>
      )}
    </Transition>
  );
};
