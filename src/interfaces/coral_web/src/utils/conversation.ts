import { Message, MessageAgent } from '@/cohere-client';
import { BotMessage, BotState, MessageType, UserMessage } from '@/types/message';
import { replaceTextWithCitations } from '@/utils/citations';
import { replaceCodeBlockWithIframe } from '@/utils/preview';

export const mapHistoryToMessages = (history?: Message[]) => {
  return history
    ? history.map<UserMessage | BotMessage>((message) => {
        const isBotMessage = message.agent === MessageAgent.CHATBOT;
        let text = message.text;
        if (isBotMessage) {
          text = replaceCodeBlockWithIframe(message.text);
        }
        return {
          ...(isBotMessage
            ? { type: MessageType.BOT, state: BotState.FULFILLED, originalText: message.text ?? '' }
            : { type: MessageType.USER }),
          text: replaceTextWithCitations(
            text ?? '',
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
