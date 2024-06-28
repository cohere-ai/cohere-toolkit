import { Message, MessageAgent } from '@/cohere-client';
import { BotState, FulfilledMessage, MessageType, UserMessage } from '@/types/message';
import { replaceTextWithCitations } from '@/utils/citations';
import { replaceCodeBlockWithIframe } from '@/utils/preview';

type UserOrBotMessage = UserMessage | FulfilledMessage;

/**
 * @description Maps chat history given by the API to a list of messages that can be displayed in the chat.
 */
export const mapHistoryToMessages = (history?: Message[]): UserOrBotMessage[] => {
  if (!history) return [];

  let messages: UserOrBotMessage[] = [];
  let tempToolEvents: FulfilledMessage['toolEvents'];

  for (const message of history) {
    if (message.agent === MessageAgent.CHATBOT) {
      if (!message.tool_plan) {
        messages.push({
          type: MessageType.BOT,
          state: BotState.FULFILLED,
          originalText: message.text ?? '',
          text: replaceTextWithCitations(
            replaceCodeBlockWithIframe(message.text) ?? '',
            message.citations ?? [],
            message.generation_id ?? ''
          ),
          generationId: message.generation_id ?? '',
          citations: message.citations,
          toolEvents: tempToolEvents,
        });
        tempToolEvents = undefined;
      } else {
        // Historical tool events come in as chatbot messages before the actual final response message.
        if (tempToolEvents) {
          tempToolEvents.push({
            text: message.tool_plan,
            tool_calls: message.tool_calls,
          });
        } else {
          tempToolEvents = [{ text: message.tool_plan, tool_calls: message.tool_calls }];
        }
      }
    } else {
      messages.push({
        type: MessageType.USER,
        text: replaceTextWithCitations(
          message.text ?? '',
          message.citations ?? [],
          message.generation_id ?? ''
        ),
        files: message.files,
      });
    }
  }

  return messages;
};
