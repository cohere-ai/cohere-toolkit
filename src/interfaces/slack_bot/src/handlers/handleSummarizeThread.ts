import { AllMiddlewareArgs, Context, MessageEvent, RespondFn, SayFn } from '@slack/bolt';

import { ApiError, OpenAPI, ToolkitClient } from '../cohere-client';
import { ALERTS, DEPLOYMENT_COHERE_PLATFORM, ERRORS, PROMPTS } from '../constants';
import { getEphemeralBlocks } from '../utils/getMessageBlocks';
import { getSanitizedConversationHistory } from '../utils/getSanitizedConversationHistory';
import { handleError } from './';

type HandleSummarizeThreadArgs = Pick<AllMiddlewareArgs, 'client'> & {
  context: Context;
  userId: string;
  threadChannelId: string;
  threadTs: string;
  say: SayFn | RespondFn;
  currentChannelId?: string;
  deployment?: string | null;
  model?: string | null;
};

/**
 * This function deals with providing a summary of a thread passed down to it.
 * It also handles the edge cases of the thread not having enough characters to summarize,
 * and posts helper ephemeral message(s)
 *
 */
export const handleSummarizeThread = async ({
  context,
  userId,
  client,
  threadChannelId,
  threadTs,
  say,
  currentChannelId,
  deployment,
  model,
}: HandleSummarizeThreadArgs) => {
  /**
   * If a currentChannelId is provided, the reply can be posted in that channel,
   * otherwise post in the thread.
   */
  const replyChannelId = currentChannelId || threadChannelId;
  const replyThreadTs = currentChannelId ? undefined : threadTs;

  /**
   * Conversation Replies Method - https://api.slack.com/methods/conversations.replies
   * Retrieve all thread replies using slack api
   */
  const basicErrorHandlerArgs = { client, userId, replyChannelId, replyThreadTs };
  const slackMessageHistoryResponse = await client.conversations
    .replies({
      channel: threadChannelId,
      ts: threadTs,
    })
    .catch(async (error) => await handleError({ error, ...basicErrorHandlerArgs }));

  if (!slackMessageHistoryResponse) return;

  /**
   * We want to avoid summarizing private conversation
   * threads that the user is not a part of
   */
  const channelHasCurrentUser = await client.conversations
    .members({
      channel: threadChannelId,
    })
    .then((data) => data.members?.includes(userId))
    .catch(async (error) => await handleError({ error, ...basicErrorHandlerArgs }));

  const isConvoPrivate = await client.conversations
    .info({ channel: threadChannelId })
    .then((data) => data.channel && data.channel.is_private)
    .catch(async (error) => await handleError({ error, ...basicErrorHandlerArgs }));

  if (!channelHasCurrentUser && isConvoPrivate) {
    await handleError({
      customErrorMsg: ERRORS.USER_NOT_IN_CHANNEL,
      ...basicErrorHandlerArgs,
      includeUserIdInMsg: false,
    });
    return;
  }

  const messageHistory = slackMessageHistoryResponse.messages;
  const { sanitizedConversationHistoryString } = await getSanitizedConversationHistory({
    context,
    client,
    // the "as" is needed to convert back to Bolt types
    messageHistory: messageHistory as Array<MessageEvent>,
    format: 'string',
  });

  //Summarize endpoint requires at least 500 characters
  if (sanitizedConversationHistoryString && sanitizedConversationHistoryString.length < 500) {
    await handleError({
      customErrorMsg: ERRORS.SUMMARIZE_CHAR_LIMIT,
      ...basicErrorHandlerArgs,
    });
    return;
  }

  // Post an ephemeral message to the user notifying them that the command is registered
  try {
    await client.chat.postEphemeral({
      text: `<@${userId}> ${ALERTS.SUMMARIZE_COMMAND_REGISTERED}`,
      blocks: getEphemeralBlocks({
        text: `<@${userId}> ${ALERTS.SUMMARIZE_COMMAND_REGISTERED}`,
        isDismissible: false,
      }),
      thread_ts: replyThreadTs,
      channel: replyChannelId,
      user: userId,
    });
  } catch (error) {
    console.error(error);
  }
  try {
    const toolkitClient = new ToolkitClient(OpenAPI);
    const summaryResponse = await toolkitClient.default.chatV1ChatPost({
      requestBody: {
        message: PROMPTS.summarizeThread(sanitizedConversationHistoryString as string),
        model,
      },
      deploymentName: deployment ? deployment : DEPLOYMENT_COHERE_PLATFORM,
    });
    /**
     * If we're not posting in the original thread,(currentChannelId is provided)
     * we want to provide a link to the original thread for reference
     */
    const originalThreadLink = currentChannelId
      ? `\n:link: <https://app.slack.com/archives/${threadChannelId}/p${threadTs
          .split('.')
          .join('')}|Original thread>`
      : '';

    await say({
      response_type: 'in_channel',
      text: `${ALERTS.THREAD_SUMMARY_PREFIX}${originalThreadLink}\n\n${summaryResponse.text}\n\ncc: <@${userId}>`,
      thread_ts: replyThreadTs,
    });
  } catch (error) {
    console.error(error);
    let customErrorMsg = ERRORS.SUMMARIZE;
    if (error instanceof ApiError) {
      customErrorMsg = error.message;
    }
    await handleError({
      customErrorMsg,
      ...basicErrorHandlerArgs,
    });
    return;
  }
};
