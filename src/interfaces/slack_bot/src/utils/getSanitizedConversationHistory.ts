import { AllMiddlewareArgs, AppMentionEvent, Context, MessageEvent } from '@slack/bolt';

import { ALERTS, STOP_REPLYING_MESSAGE } from '../constants';
import { getSanitizedMessage } from './getSanitizedMessage';
import { GetUsersRealNameArgs, getUsersRealName } from './getUsersRealName';

type Message = MessageEvent | AppMentionEvent;

type ChatlogMessage = {
  user_name: string;
  message: string;
};

type GetSanitizedConversationHistoryArgs = Pick<AllMiddlewareArgs, 'client'> & {
  context: Context;
  messageHistory: Array<Message>;
  format?: 'object' | 'string';
  isDM?: boolean;
};

type SanitizedConversationHistoryArray = {
  sanitizedConversationHistory: Array<ChatlogMessage>;
  sanitizedConversationHistoryString?: string;
};

type SanitizedConversationHistoryString = {
  sanitizedConversationHistory?: Array<ChatlogMessage>;
  sanitizedConversationHistoryString: string;
};

type SanitizedConversationHistory = {
  hasStopReplyingCommand: boolean;
  hasBotAckStopReplyingCommand: boolean;
} & (SanitizedConversationHistoryArray | SanitizedConversationHistoryString);

/**
 * Accepts a slack formatted message history and re-formats
 * it in a way that can be used for /chat endpoint or /summarize endpoint
 */
export const getSanitizedConversationHistory = async ({
  context,
  client,
  messageHistory,
  format = 'object',
  isDM = false,
}: GetSanitizedConversationHistoryArgs): Promise<SanitizedConversationHistory> => {
  const botUserId = context.botUserId;
  const botId = context.botId;

  const hasStopReplyingCommand = messageHistory.some(
    (msg: any) =>
      msg.text.includes(`<@${botUserId}> chill`) ||
      msg.text.toLowerCase().includes('command chill'),
  );

  const hasBotAckStopReplyingCommand = messageHistory.some(
    (msg: any) => msg.user === botUserId && msg.text === STOP_REPLYING_MESSAGE,
  );

  // Exclude all bot messages that aren't command
  const userAndCommandMessages = messageHistory.filter(
    (msg: Message) =>
      (msg.subtype === 'bot_message' && msg.bot_id !== botId) || msg.subtype !== 'bot_message',
  );

  // Get all the usernames in the conversation
  const usernames: { [key: string]: string } = {};
  for (let msg of userAndCommandMessages) {
    /**
     * Since user exists on both AppMentionEvent and MessageEvent,
     * we can safely cast to AppMentionEvent to avoid TS errors
     */
    msg = msg as AppMentionEvent;
    if (msg.user && !usernames[msg.user]) {
      const userInfo = await client.users.info({
        user: msg.user,
      });

      usernames[msg.user] = userInfo.user?.profile?.display_name ?? 'user';
    }
  }

  const chunkedMarkerRegex = /(\[\d+\/\d+\] )/g;

  const userAndCommandMessagesWithoutChunkedMarkers = userAndCommandMessages.map((msg: any) => {
    if (msg.text) {
      msg.text = msg.text.replaceAll(chunkedMarkerRegex, '');
    }

    for (const block of msg.blocks || []) {
      if (block.type !== 'section' || block.text.type !== 'mrkdwn') continue;
      block.text.text = block.text.text.replaceAll(chunkedMarkerRegex, '');
    }

    return msg;
  });

  // Used for summarize endpoint
  if (format === 'string') {
    // We don't want to include the previous summary in the convo when we make a new summary.
    const userAndCommandMessagesWithoutSummaries =
      userAndCommandMessagesWithoutChunkedMarkers.filter(
        (msg: any) => !msg.text.includes(ALERTS.THREAD_SUMMARY_PREFIX),
      );

    const sanitizedConversationHistoryStringArr = await Promise.all(
      userAndCommandMessagesWithoutSummaries.map(async (msg: any, index) => {
        if (msg.user === botUserId) {
          return `chatbot: ${msg.text}`;
        }
        const sanitizedMessage = await getSanitizedMessage({
          message: msg.text,
          getUsersRealName: async ({ userId }: GetUsersRealNameArgs) =>
            getUsersRealName({ userId, client }),
          botUserId,
          isFirstMessage: !isDM && index === 0,
        });
        return `${usernames[msg.user]}: ${sanitizedMessage}`;
      }),
    );

    // Combine consecutive messages from the same username into one message
    // This is to avoid breaking internal tools that expect one message per user per conversation turn
    const combinedMessagesStringArr = sanitizedConversationHistoryStringArr.reduce((acc, curr) => {
      let lastMessage = acc[acc.length - 1];

      if (lastMessage && lastMessage.startsWith(curr.split(':')[0])) {
        const currMsgTextWithoutUsername = curr.split(':').slice(1).join(':');
        // Directly mutate the last message in the array since JS/TS is pass-by-value
        acc[acc.length - 1] = `${lastMessage}\n${currMsgTextWithoutUsername}`;
        return acc;
      }

      return [...acc, curr];
    }, [] as Array<string>);

    const combinedMessagesString = combinedMessagesStringArr.join('\n');

    return {
      sanitizedConversationHistoryString: combinedMessagesString,
      hasStopReplyingCommand,
      hasBotAckStopReplyingCommand,
    };
  }

  /**
   * Follow the format /chat endpoint expects and remove the most recent message.
   * The endpoint expects that as a separate argument.
   */
  const sanitizedConversationHistory = await Promise.all(
    userAndCommandMessagesWithoutChunkedMarkers
      .map(async (msg: any, index) => {
        // If there's a block with markdown, use that. Otherwise, use the non-markdown text
        const originalMessage = msg.blocks?.[0]?.text?.text || msg.text;

        if (msg.user === botUserId || msg.subtype === 'bot_message') {
          // remove any text related to RAG sources from the history
          const msgWithoutSources = originalMessage.split(ALERTS.RAG_SOURCES_PREFIX)[0];
          return { user_name: 'Chatbot', message: msgWithoutSources };
        }

        const sanitizedMessage = await getSanitizedMessage({
          message: originalMessage,
          getUsersRealName: async ({ userId }: GetUsersRealNameArgs) =>
            getUsersRealName({ userId, client }),
          botUserId,
          isFirstMessage: !isDM && index === 0,
        });

        return { user_name: 'User', message: sanitizedMessage };
      })
      .slice(0, -1),
  );

  // Combine consecutive messages from the same user into one message
  // This is to avoid breaking internal tools that expect one message per user per conversation turn
  const combinedMessages = sanitizedConversationHistory.reduce((acc, curr) => {
    const lastMessage = acc[acc.length - 1];

    if (lastMessage && lastMessage.user_name === curr.user_name) {
      lastMessage.message = `${lastMessage.message}\n${curr.message}`;
      return acc;
    }

    return [...acc, curr];
  }, [] as Array<ChatlogMessage>);

  return {
    sanitizedConversationHistory: combinedMessages,
    hasStopReplyingCommand,
    hasBotAckStopReplyingCommand,
  };
};
