import { Middleware, SlackCommandMiddlewareArgs } from '@slack/bolt';

import { ALERTS } from '../constants';
import { handleError, handleSummarizeThread } from '../handlers';
import { getChannelSettings } from '../utils/getChannelSettings';

/**
 * This slash command can be used in dms, groups and channels to
 * get a summary of a thread given a link
 */
export const summarize: Middleware<SlackCommandMiddlewareArgs> = async ({
  ack,
  respond,
  command,
  client,
  context,
}) => {
  await ack();
  /**
   * Extracts the thread channel id and thread time-stamp from the link
   * channel -> C02L95WDEKA
   * thread_ts -> p1675178802502139 -> 1675178802.502139
   */
  const threadChannelId = command.text.match(/(C|D)\w{10}/g)?.[0];

  const unformattedTs = command.text.match(/p\d{16}/g)?.[0];
  // Thread TS always has 6 numbers after the decimal; The number of numbers before the decimal varies
  const threadTs = unformattedTs?.replace(/(\d+)(\d{6})/g, '$1.$2');
  const userId = command.user_id;
  const channelId = command.channel_id;
  const teamId = context.teamId;
  const enterpriseId = context.enterpriseId;

  // Not an valid slack thread link
  if (!threadChannelId || !threadTs) {
    await handleError({
      client,
      customErrorMsg: ALERTS.NOT_SLACK_THREAD_LINK,
      userId,
      replyChannelId: channelId,
      includeUserIdInMsg: false,
    });
    return;
  }
  const { deployment, model, temperature, preambleOverride } = await getChannelSettings({
    teamId,
    enterpriseId,
    channelId,
  });

  await handleSummarizeThread({
    context,
    client,
    threadChannelId,
    userId,
    threadTs,
    say: respond,
    currentChannelId: channelId,
    deployment,
    model,
  });
};
