import { Middleware, SlackCommandMiddlewareArgs } from '@slack/bolt';

import { ALERTS } from '../constants';
import { getChannelSettings } from '../utils/getChannelSettings';
import { getEphemeralBlocks } from '../utils/getMessageBlocks';

export const viewDeployment: Middleware<SlackCommandMiddlewareArgs> = async ({
  context,
  ack,
  respond,
  command,
}) => {
  await ack();

  const channelId = command.channel_id;
  const channelName = command.channel_name;

  const { deployment } = await getChannelSettings({
    teamId: context.teamId,
    enterpriseId: context.enterpriseId,
    channelId,
  });

  await respond({
    response_type: 'ephemeral',
    text: ALERTS.channelDeploymentView(channelName, deployment),
    blocks: getEphemeralBlocks({ text: ALERTS.channelDeploymentView(channelName, deployment) }),
  });
};
