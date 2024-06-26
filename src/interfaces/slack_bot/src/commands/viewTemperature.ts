import { Middleware, SlackCommandMiddlewareArgs } from '@slack/bolt';

import { ALERTS, DEFAULT_CHAT_TEMPERATURE } from '../constants';
import { getChannelSettings } from '../utils/getChannelSettings';
import { getEphemeralBlocks } from '../utils/getMessageBlocks';

export const viewTemperature: Middleware<SlackCommandMiddlewareArgs> = async ({
  context,
  ack,
  respond,
  command,
}) => {
  await ack();

  const channelId = command.channel_id;
  const channelName = command.channel_name;

  let { temperature } = await getChannelSettings({
    teamId: context.teamId,
    enterpriseId: context.enterpriseId,
    channelId,
  });

  temperature = temperature || DEFAULT_CHAT_TEMPERATURE;

  await respond({
    response_type: 'ephemeral',
    text: ALERTS.channelTemperatureView(channelName, temperature),
    blocks: getEphemeralBlocks({
      text: ALERTS.channelTemperatureView(channelName, temperature),
    }),
  });
};
