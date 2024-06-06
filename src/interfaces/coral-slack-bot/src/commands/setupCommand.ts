import { KnownBlock, Middleware, SlackCommandMiddlewareArgs } from '@slack/bolt';

import { prisma } from '..';
import { ALERTS } from '../constants';
import { handleError } from '../handlers';

// API Key Commands, brings up a modal for user to input api key
export const setupCommand: Middleware<SlackCommandMiddlewareArgs> = async ({
  client,
  ack,
  respond,
  command,
  context,
  body,
}) => {
  await ack();

  const userInfo = await client.users.info({ user: command.user_id });
  const userIsAdmin = userInfo.user ? userInfo.user.is_admin || userInfo.user.is_owner : false;

  await prisma.workspaceSettings.upsert({
    create: { teamId: context.teamId, enterpriseId: context.enterpriseId },
    update: {},
    where: { teamId: context.teamId, enterpriseId: context.enterpriseId },
  });

  if (!userIsAdmin && process.env.NODE_ENV !== 'development') {
    await respond({
      response_type: 'ephemeral',
      text: ALERTS.NOT_ADMIN,
    });
    return;
  }

  const blocks = [
    {
      type: 'section',
      block_id: 'intro_block',
      text: {
        type: 'mrkdwn',
        text: "Hello! 👋 Let's get Command setup!",
      },
    },
    {
      type: 'section',
      block_id: 'legal_block',
      text: {
        type: 'mrkdwn',
        text: "By submitting this form, you agree to Cohere's <https://cohere.com/terms-of-use|Terms of Use>, and <https://cohere.com/privacy|Privacy Policy>.",
      },
    },
  ].filter((n) => n) as KnownBlock[]; // Remove nulls and undefineds

  const channelId = command.channel_id;
  await client.views
    .open({
      trigger_id: body.trigger_id,
      view: {
        callback_id: 'api_view',
        // Pass whether the user is an admin to avoid duplicate DB calls
        private_metadata: JSON.stringify({ userIsAdmin }),
        title: {
          type: 'plain_text',
          text: 'Command Setup',
          emoji: true,
        },
        submit: {
          type: 'plain_text',
          text: 'Submit',
          emoji: true,
        },
        type: 'modal',
        close: {
          type: 'plain_text',
          text: 'Cancel',
          emoji: true,
        },
        blocks,
      },
    })
    .catch(
      async (error) =>
        await handleError({
          client,
          userId: command.user_id,
          replyChannelId: channelId,
          replyThreadTs: command.thread_ts,
          customErrorMsg: error,
        }),
    );
};
