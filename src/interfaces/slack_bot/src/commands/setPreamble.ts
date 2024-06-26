import { Middleware, SlackCommandMiddlewareArgs } from '@slack/bolt';

import { prisma } from '..';
import { ALERTS } from '../constants';
import { getEphemeralBlocks } from '../utils/getMessageBlocks';

// Preamble Override Commands

export const setPreamble: Middleware<SlackCommandMiddlewareArgs> = async ({
  context,
  ack,
  respond,
  command,
}) => {
  await ack();

  const channelId = command.channel_id;
  const channelName = command.channel_name;

  const preambleOverride = command.text == '' ? null : command.text;

  const workspaceSettings = await prisma.workspaceSettings.upsert({
    create: { teamId: context.teamId, enterpriseId: context.enterpriseId },
    update: {},
    where: { teamId: context.teamId, enterpriseId: context.enterpriseId },
  });

  await prisma.channelSettings.upsert({
    create: {
      channelId,
      workspaceId: workspaceSettings.id,
      preamble: preambleOverride,
    },
    update: { preamble: preambleOverride },
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
      text: ALERTS.channelPreambleOverrideSet(channelName, preambleOverride),
      blocks: getEphemeralBlocks({
        text: ALERTS.channelPreambleOverrideSet(channelName, preambleOverride),
      }),
    });
    return;
  }

  await respond({
    response_type: 'in_channel',
    text: ALERTS.channelPreambleOverrideSet(channelName, preambleOverride, command.user_id),
  });
};
