import { Middleware, SlackActionMiddlewareArgs } from '@slack/bolt';

export const dismissEphemeral: Middleware<SlackActionMiddlewareArgs> = async ({ ack, respond }) => {
  await ack();
  // Update the message to reflect the action
  await respond({
    delete_original: true,
  });
};
