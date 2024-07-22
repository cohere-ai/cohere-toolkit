'use client';

import Lottie from 'react-lottie-player';

import logoTyping from '@/assets/lotties/icon-loop-coral-950.json';
import logoTypingMushroom from '@/assets/lotties/icon-loop-coral-mushroom.json';
import { CoralLogo } from '@/components/Shared/CoralLogo';
import { Icon } from '@/components/Shared/Icon';
import { BotState, ChatMessage, MessageType, isFulfilledMessage } from '@/types/message';
import { cn } from '@/utils/cn';

type Props = {
  message: ChatMessage;
};

export const Avatar: React.FC<Props> = ({ message }) => {
  const isUser = message.type === MessageType.USER;
  const isBot = message.type === MessageType.BOT;
  const isLoading = isBot && message.state === BotState.LOADING;
  const isTyping = isBot && message.state === BotState.TYPING;
  const isErrored = isBot && message.state === BotState.ERROR;
  const isAborted = isBot && message.state === BotState.ABORTED;

  const isFulfilled = isFulfilledMessage(message);
  const isTypingOrLoading = isBot && (isTyping || isLoading);
  const isErroredOrAborted = isBot && (isErrored || isAborted);

  const hasRAGOnProperty = 'isRAGOn' in message;
  const isRAGOn = hasRAGOnProperty && Boolean(message.isRAGOn);
  // Not having the tools property means that this message is loaded from conversation history
  // and with the current info we get from the backend we don't know if it has tools or not.
  const isGroundingOn = !hasRAGOnProperty || isRAGOn;

  return (
    <div
      className={cn(
        'flex flex-shrink-0 items-center justify-center rounded text-white',
        'h-7 w-7 md:h-9 md:w-9',
        {
          'bg-volcanic-600': isErroredOrAborted,
          'bg-quartz-700': isUser,
        },
        isGroundingOn
          ? {
              'bg-coral-200': isFulfilled,
              'bg-coral-800': isTypingOrLoading,
            }
          : {
              'bg-mushroom-700': isFulfilled,
              'bg-mushroom-800': isTypingOrLoading,
            }
      )}
    >
      {isBot && (
        <BotAvatar
          state={message.state}
          style={isErroredOrAborted ? 'grayscale' : isGroundingOn ? 'primary' : 'secondary'}
        />
      )}

      {isUser && <UserAvatar />}
    </div>
  );
};

export const BotAvatar: React.FC<{
  state: BotState;
  style: React.ComponentProps<typeof CoralLogo>['style'];
}> = ({ state, style }) => {
  if (state === BotState.TYPING || state === BotState.LOADING) {
    return (
      <Lottie
        animationData={style === 'secondary' ? logoTypingMushroom : logoTyping}
        play
        loop
        className="h-5 w-5 md:h-7 md:w-7"
      />
    );
  }
  return <CoralLogo style={style} className="h-4 w-4 md:h-5 md:w-5" />;
};

const UserAvatar: React.FC = () => {
  return <Icon name="profile" className="text-icon-md text-white md:text-icon-lg" />;
};
