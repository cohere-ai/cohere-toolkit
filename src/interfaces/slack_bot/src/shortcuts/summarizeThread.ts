import { Middleware, SlackShortcutMiddlewareArgs } from '@slack/bolt';

import { handleSummarizeThread } from '../handlers';

export const summarizeThread: Middleware<SlackShortcutMiddlewareArgs> = async ({
  context,
  shortcut,
  ack,
  client,
  respond,
}) => {
  await ack();

  // Summarize shortcut is only available for message actions
  if (shortcut.type !== 'message_action') return;

  const userId = shortcut.user.id;
  // Start a new thread if the shortcut is used on the first message without any replies
  const threadTs = shortcut.message.thread_ts || shortcut.message_ts;
  const threadChannelId = shortcut.channel.id;

  await handleSummarizeThread({
    context,
    client,
    threadChannelId,
    userId,
    threadTs,
    say: respond,
  });
};
