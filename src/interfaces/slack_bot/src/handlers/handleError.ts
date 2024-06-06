import { AllMiddlewareArgs } from '@slack/bolt';

import { ERRORS, SLACK_API_ERRORS } from '../constants';
import { getEphemeralBlocks } from '../utils/getMessageBlocks';

type HandleError = Pick<AllMiddlewareArgs, 'client'> & {
  error?: any;
  userId?: string;
  includeUserIdInMsg?: boolean;
  replyChannelId?: string;
  replyThreadTs?: string;
  customErrorMsg?: string;
  messageTs?: string;
};

/**
 * This function does basic error handling in the form of posting an ephemeral
 * message to the user to notify them that something's not right.
 * This includes; handling slack api errors, cohere API error and other general errors.
 */
export const handleError = async ({
  error,
  userId,
  includeUserIdInMsg = true,
  replyChannelId,
  replyThreadTs,
  client,
  customErrorMsg,
  messageTs,
}: HandleError) => {
  // Return early if user unknown - ephemeral message are only visible to the user,
  if (!userId) return;

  const errorMsg = customErrorMsg || SLACK_API_ERRORS[error?.data?.error] || ERRORS.GENERAL;
  const formattedUserId = includeUserIdInMsg ? `<@${userId}> ` : '';
  /**
   * Try to post an error message in the channel the event occurred in,
   * If that fails, try to send a DM to the user.
   * Common Error response from slack: https://api.slack.com/methods/conversations.replies#examples
   */

  const slackResponse =
    replyChannelId &&
    (await client.chat
      .postEphemeral({
        text: `${formattedUserId}${errorMsg}`,
        blocks: getEphemeralBlocks({ text: `${formattedUserId}${errorMsg}` }),
        thread_ts: replyThreadTs,
        channel: replyChannelId,
        user: userId,
      })
      .catch((errorRes) => console.error(errorRes)));

  if (!slackResponse) {
    await client.chat
      .postEphemeral({
        text: errorMsg,
        channel: userId,
        user: userId,
      })
      .catch((errorRes) => console.error(errorRes));
  }
  if (messageTs)
    await client.reactions
      .add({
        channel: replyChannelId,
        name: 'warning',
        timestamp: messageTs,
      })
      .catch((errorRes) => console.error(errorRes));
};
