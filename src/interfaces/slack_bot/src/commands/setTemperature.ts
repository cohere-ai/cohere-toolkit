import { Middleware, SlackCommandMiddlewareArgs } from '@slack/bolt';

import { prisma } from '..';
import { ALERTS, DEFAULT_CHAT_TEMPERATURE, ERRORS } from '../constants';
import { handleError } from '../handlers';
import { getEphemeralBlocks } from '../utils/getMessageBlocks';

// Channel Temperature Commands
export const setTemperature: Middleware<SlackCommandMiddlewareArgs> = async ({
  client,
  context,
  ack,
  respond,
  command,
}) => {
  await ack();

  const channelId = command.channel_id;
  const channelName = command.channel_name;

  const temperature = command.text ? Number(command.text) : DEFAULT_CHAT_TEMPERATURE;

  if (isNaN(temperature) || temperature < 0 || temperature > 5) {
    await handleError({
      client,
      userId: command.user_id,
      replyChannelId: channelId,
      replyThreadTs: command.thread_ts,
      customErrorMsg: ERRORS.INVALID_TEMPERATURE,
    });
    return;
  }

  const workspaceSettings = await prisma.workspaceSettings.upsert({
    create: { teamId: context.teamId, enterpriseId: context.enterpriseId },
    update: {},
    where: { teamId: context.teamId, enterpriseId: context.enterpriseId },
  });

  await prisma.channelSettings.upsert({
    create: {
      channelId,
      workspaceId: workspaceSettings.id,
      temperature,
    },
    update: { temperature },
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
      text: ALERTS.channelTemperatureSet(channelName, temperature),
      blocks: getEphemeralBlocks({
        text: ALERTS.channelTemperatureSet(channelName, temperature),
      }),
    });
    return;
  }

  await respond({
    response_type: 'in_channel',
    text: ALERTS.channelTemperatureSet(channelName, temperature, command.user_id),
  });
};
