'use client';

import { Citation } from '@/components/Citations/Citation';
import { CitationToStyles } from '@/hooks/citations';
import { useConversationStore } from '@/stores';
import { ChatMessage, isFulfilledOrTypingMessage } from '@/types/message';

type Props = {
  streamingMessage: ChatMessage | null;
  citationToStyles?: CitationToStyles;
  className?: string;
};

export const CitationPanel: React.FC<Props> = ({ streamingMessage, citationToStyles }) => {
  const {
    conversation: { messages },
  } = useConversationStore();

  return (
    <div className="flex-grow flex-col gap-y-2 md:items-end lg:items-center">
      <div className="relative flex h-full w-full flex-col gap-y-2 pb-12 pt-1">
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
    </div>
  );
};
