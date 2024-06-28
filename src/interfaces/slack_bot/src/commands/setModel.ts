import { Middleware, SlackCommandMiddlewareArgs } from '@slack/bolt';

import { prisma } from '..';
import { ALERTS } from '../constants';
import { getEphemeralBlocks } from '../utils/getMessageBlocks';

// Channel Model Commands
export const setModel: Middleware<SlackCommandMiddlewareArgs> = async ({
  context,
  ack,
  respond,
  command,
}) => {
  await ack();

  const channelId = command.channel_id;
  const channelName = command.channel_name;

  const modelName = command.text || null;
  const workspaceSettings = await prisma.workspaceSettings.upsert({
    create: { teamId: context.teamId, enterpriseId: context.enterpriseId },
    update: {},
    where: { teamId: context.teamId, enterpriseId: context.enterpriseId },
  });

  await prisma.channelSettings.upsert({
    create: {
      channelId,
      workspaceId: workspaceSettings.id,
      modelName,
    },
    update: { modelName },
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
      text: ALERTS.channelModelSet(channelName, modelName),
      blocks: getEphemeralBlocks({
        text: ALERTS.channelModelSet(channelName, modelName),
      }),
    });
    return;
  }

  await respond({
    response_type: 'in_channel',
    text: ALERTS.channelModelSet(channelName, modelName, command.user_id),
  });
};
