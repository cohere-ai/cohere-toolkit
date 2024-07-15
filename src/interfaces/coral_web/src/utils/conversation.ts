import { Message, MessageAgent } from '@/cohere-client';
import { BotState, ChatMessage, FulfilledMessage, MessageType, UserMessage } from '@/types/message';
import { replaceTextWithCitations } from '@/utils/citations';
import { replaceCodeBlockWithIframe } from '@/utils/preview';

/**
 * A utility function that checks if the conversation title should be updated
 * Based on:
 *  - It has only two messages, one from the user and one from the bot.
 *  - If ~5 turns have passed, meaning every 5 messages from the bot.
 *    - Note: the bot can fail to respond and these turns can become out of sync but 5 bot messages
 *      implies that there were at least 5 matching user messages (user message === request, bot message === response pairs)
 * @param messages - The messages array
 * */
export const shouldUpdateConversationTitle = (messages: ChatMessage[]) => {
  const numUserMessages = messages.filter(
    (message) => message.type === MessageType.USER && !message.error
  ).length;
  const numBotMessages = messages.filter(
    (message) => message.type === MessageType.BOT && message.state === BotState.FULFILLED
  ).length;

  if (numUserMessages === 1 && numBotMessages === 1) {
    return true;
  }

  return numBotMessages % 5 === 0;
};

export type UserOrBotMessage = UserMessage | FulfilledMessage;

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
