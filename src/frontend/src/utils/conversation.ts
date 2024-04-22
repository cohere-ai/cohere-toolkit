import { Message, MessageAgent } from '@/cohere-client';
import { BotMessage, BotState, MessageType, UserMessage } from '@/types/message';
import { replaceTextWithCitations } from '@/utils/citations';

export const mapHistoryToMessages = (history?: Message[]) => {
  return history
    ? history.map<UserMessage | BotMessage>((message) => {
        return {
          ...(message.agent === MessageAgent.CHATBOT
            ? { type: MessageType.BOT, state: BotState.FULFILLED, originalText: message.text ?? '' }
            : { type: MessageType.USER }),
          text: replaceTextWithCitations(
            message.text ?? '',
            message.citations ?? [],
            message.generation_id ?? ''
          ),
          generationId: message.generation_id ?? '',
          citations: message.citations,
          files: message.files,
        };
      })
    : [];
};
