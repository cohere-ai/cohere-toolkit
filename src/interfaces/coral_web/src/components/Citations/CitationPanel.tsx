'use client';

import { Transition } from '@headlessui/react';

import { Citation } from '@/components/Citations/Citation';
import { CitationToStyles } from '@/hooks/citations';
import { useCitationsStore, useConversationStore } from '@/stores';
import { ChatMessage, isFulfilledOrTypingMessage } from '@/types/message';
import { cn } from '@/utils';

type Props = {
  streamingMessage: ChatMessage | null;
  citationToStyles?: CitationToStyles;
  className?: string;
};

export const CitationPanel: React.FC<Props> = ({
  streamingMessage,
  citationToStyles,
  className = '',
}) => {
  const {
    citations: { hasCitations },
  } = useCitationsStore();
  const {
    conversation: { messages },
  } = useConversationStore();

  return (
    <Transition
      show={hasCitations}
      appear
      enter="transition-opacity delay-1000 ease-in-out duration-1000"
      enterFrom="opacity-0"
      enterTo="opacity-100"
      as="div"
      className={cn('h-auto flex-col gap-y-2 md:items-end lg:items-center', className)}
    >
      <div className="relative flex h-full w-full flex-col gap-y-2 overflow-hidden pb-12 pt-1">
        <>
          {messages.map((message) => {
            if (
              isFulfilledOrTypingMessage(message) &&
              message.citations &&
              message.citations.length > 0
            ) {
              const generationId = message.generationId;
              return (
                <Citation
                  key={generationId}
                  generationId={generationId}
                  message={message.originalText}
                  styles={citationToStyles?.[generationId]}
                />
              );
            }
            return null;
          })}
          {streamingMessage &&
            isFulfilledOrTypingMessage(streamingMessage) &&
            citationToStyles?.[streamingMessage.generationId] && (
              <Citation
                key={streamingMessage.generationId}
                generationId={streamingMessage.generationId}
                isLastStreamed={true}
                message={streamingMessage.originalText}
                styles={citationToStyles?.[streamingMessage.generationId]}
              />
            )}
        </>
      </div>
    </Transition>
  );
};
