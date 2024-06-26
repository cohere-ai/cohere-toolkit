import { Middleware, SlackActionMiddlewareArgs } from '@slack/bolt';

import { handleStopConversation } from '../handlers';

export const stopConversation: Middleware<SlackActionMiddlewareArgs> = async ({
  client,
  ack,
  body,
  respond,
}) => handleStopConversation({ client, ack, body, respond });
