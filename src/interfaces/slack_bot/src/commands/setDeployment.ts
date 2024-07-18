import { Middleware, SlackCommandMiddlewareArgs } from '@slack/bolt';

import { prisma } from '..';
import { ALERTS } from '../constants';
import { getEphemeralBlocks } from '../utils/getMessageBlocks';

// Channel Model Commands
export const setDeployment: Middleware<SlackCommandMiddlewareArgs> = async ({
  context,
  ack,
  respond,
  command,
}) => {
  await ack();

  const channelId = command.channel_id;
  const channelName = command.channel_name;

  const deployment = command.text || null;
  const workspaceSettings = await prisma.workspaceSettings.upsert({
    create: { teamId: context.teamId, enterpriseId: context.enterpriseId },
    update: {},
    where: { teamId: context.teamId, enterpriseId: context.enterpriseId },
  });

  await prisma.channelSettings.upsert({
    create: {
      channelId,
      workspaceId: workspaceSettings.id,
      deployment,
    },
    update: { deployment },
    where: {
      channelSettingsId: {
        channelId,
        workspaceId: workspaceSettings.id,
      },
    },
  });

  if (command.channel_name === 'directmessage') {
    await respond({
      response_type: 'ephemeral',
      text: ALERTS.channelDeploymentSet(channelName, deployment),
      blocks: getEphemeralBlocks({
        text: ALERTS.channelDeploymentSet(channelName, deployment),
      }),
    });
    return;
  }

  await respond({
    response_type: 'in_channel',
    text: ALERTS.channelDeploymentSet(channelName, deployment, command.user_id),
  });
};
