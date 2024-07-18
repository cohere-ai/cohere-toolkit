import { Middleware, SlackCommandMiddlewareArgs } from '@slack/bolt';
import { getChannelSettings } from 'src/utils/getChannelSettings';

import { ApiError, OpenAPI, ToolkitClient } from '../cohere-client';
import { ERRORS } from '../constants';
import { handleError } from '../handlers';
import { getEphemeralBlocks } from '../utils/getMessageBlocks';

// Shows users the tools enabled for a channel or all tools available
export const viewTools: Middleware<SlackCommandMiddlewareArgs> = async ({
  ack,
  client,
  context,
  command,
  respond,
}) => {
  await ack();

  const basicErrorHandlerArgs = {
    client,
    userId: command.user_id,
    replyChannelId: command.channel_id,
  };

  //can be all or channel, defaults to channel
  const toolsToList = command.text === 'all' ? 'all' : 'channel';

  if (toolsToList === 'channel') {
    const channelId = command.channel_id;

    const { tools } = await getChannelSettings({
      teamId: context.teamId,
      enterpriseId: context.enterpriseId,
      channelId,
    });

    const toolsMessage =
      tools.length > 0
        ? `Here are the tools enabled for this channel: \n${tools
            .map((t) => `• ${t.name}`)
            .join('\n')}`
        : 'No tools have been enabled for this channel. \nYou can set tools using the command `/set-tools`';

    await respond({
      response_type: 'ephemeral',
      text: toolsMessage,
      blocks: getEphemeralBlocks({ text: toolsMessage }),
    });
    return;
  }

  try {
    const toolkitClient = new ToolkitClient(OpenAPI);
    const tools = await toolkitClient.default.listToolsV1ToolsGet();
    // only show active tools that do not use oauth
    const toolList = tools
      .filter((tool) => tool.is_available)
      .map((tool) => `• ${tool.name}`)
      .join('\n');

    await respond({
      response_type: 'ephemeral',
      text: `Here are all the tools available to you:\n\n${toolList}`,
      blocks: getEphemeralBlocks({
        text: `Here are all the tools available to you:\n\n${toolList}`,
      }),
    });
  } catch (error: any) {
    console.error(error);
    let customErrorMsg = ERRORS.GENERAL;
    if (error instanceof ApiError) {
      customErrorMsg = error.message;
    }
    await handleError({
      customErrorMsg: `${ERRORS.PREFIX} ${customErrorMsg}`,
      ...basicErrorHandlerArgs,
    });
    return;
  }
};
