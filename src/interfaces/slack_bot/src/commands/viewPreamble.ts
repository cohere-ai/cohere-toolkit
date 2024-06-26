import { Middleware, SlackCommandMiddlewareArgs } from '@slack/bolt';

import { ALERTS } from '../constants';
import { getChannelSettings } from '../utils/getChannelSettings';
import { getEphemeralBlocks } from '../utils/getMessageBlocks';

export const viewPreamble: Middleware<SlackCommandMiddlewareArgs> = async ({
  context,
  ack,
  respond,
  command,
}) => {
  await ack();

  const channelId = command.channel_id;
  const channelName = command.channel_name;

  const { preambleOverride } = await getChannelSettings({
    teamId: context.teamId,
    enterpriseId: context.enterpriseId,
    channelId,
  });

  await respond({
    response_type: 'ephemeral',
    text: ALERTS.channelPreambleOverrideView(channelName, preambleOverride),
    blocks: getEphemeralBlocks({
      text: ALERTS.channelPreambleOverrideView(channelName, preambleOverride),
    }),
  });
};
