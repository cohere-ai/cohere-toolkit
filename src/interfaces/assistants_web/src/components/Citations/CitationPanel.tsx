'use client';

import { Citation } from '@/components/Citations/Citation';
import { useCalculateCitationStyles } from '@/hooks/citations';
import { useConversationStore } from '@/stores';
import { useStreamingStore } from '@/stores/streaming';
import { isFulfilledOrTypingMessage } from '@/types/message';

type Props = {};

export const CitationPanel: React.FC<Props> = () => {
  const {
    conversation: { messages },
  } = useConversationStore();
  const { streamingMessage } = useStreamingStore();
  const { citationToStyles } = useCalculateCitationStyles(messages, streamingMessage);

  return (
    <div className="h-full flex-grow flex-col gap-y-2 md:items-end lg:items-center">
      <div className="relative flex h-full w-full flex-col gap-y-2 pb-12 pl-2 pt-1">
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
      </div>
    </div>
  );
};
