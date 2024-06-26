import { Middleware, SlackViewMiddlewareArgs } from '@slack/bolt';

import { prisma } from '..';

/**
 * API View
 *
 * This view is called when the user submits the form on the setupCommand modal. It handles saving
 * workspace settings to the db.
 */
export const apiView: Middleware<SlackViewMiddlewareArgs> = async ({ ack, context }) => {
  await ack({
    response_action: 'update',
    view: {
      callback_id: 'api_view_success',
      title: {
        type: 'plain_text',
        text: 'Command Setup',
        emoji: true,
      },
      type: 'modal',
      close: {
        type: 'plain_text',
        text: 'Close',
        emoji: true,
      },
      blocks: [
        {
          type: 'section',
          block_id: 'intro_block',
          text: {
            type: 'mrkdwn',
            text: "You're all set! 🎉",
          },
        },
        {
          type: 'section',
          block_id: 'description_block',
          text: {
            type: 'mrkdwn',
            text: 'Start a conversation with Command using *@Command*! To see what else Command offers, run the `/command-help` command!',
          },
        },
      ],
    },
  });

  // Save Slack workspace settings to DB.
  await prisma.workspaceSettings.upsert({
    create: {
      teamId: context.teamId,
      enterpriseId: context.enterpriseId,
    },
    update: {},
    where: { teamId: context.teamId, enterpriseId: context.enterpriseId },
  });
};
