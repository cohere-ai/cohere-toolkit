import { Middleware, SlackCommandMiddlewareArgs } from '@slack/bolt';

import { HELP_MESSAGE } from '../constants';
import { getEphemeralBlocks } from '../utils/getMessageBlocks';

/**
 * Help command to show the user how to use the bot
 * Discusses the following:
 * - What the bot can do
 * - What commands are available to the user
 * - What context menu options are available to the user
 */
export const commandHelp: Middleware<SlackCommandMiddlewareArgs> = async ({ ack, respond }) => {
  await ack();
  await respond({
    response_type: 'ephemeral',
    text: HELP_MESSAGE,
    blocks: getEphemeralBlocks({ text: HELP_MESSAGE }),
  });
};
