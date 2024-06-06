import { KnownEventFromType } from '@slack/bolt';
import { WebClient } from '@slack/web-api';

import { handleError } from '../handlers';
import { SlackMessages } from './actions';

/**
 * Conversation Replies Method - https://api.slack.com/methods/conversations.replies
 * Retrieve all thread replies using slack api
 */
export const extractMessageHistory = async (
  client: WebClient,
  event: KnownEventFromType<'message'>,
) => {
  let messages: SlackMessages = [];
  if ('thread_ts' in event && event.thread_ts) {
    try {
      const conversations = await client.conversations.replies({
        channel: event.channel,
        ts: event.thread_ts,
      });
      messages = conversations.messages || [];
    } catch (error) {
      await handleError({
        error,
        client,
        userId: event.user,
        replyChannelId: event.channel,
        replyThreadTs: event.thread_ts,
      });
    }
  }
  return messages;
};
