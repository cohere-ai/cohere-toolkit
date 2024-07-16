import { KnownBlock, Middleware, MrkdwnOption, SlackCommandMiddlewareArgs } from '@slack/bolt';

import { ApiError, OpenAPI, ToolkitClient } from '../cohere-client';
import { ERRORS } from '../constants';
import { handleError } from '../handlers';
import { getChannelSettings } from '../utils/getChannelSettings';

// Tools list command, brings up a modal for user to select tools
export const setTools: Middleware<SlackCommandMiddlewareArgs> = async ({
  client,
  ack,
  respond,
  command,
  context,
  body,
}) => {
  await ack();

  const channelId = command.channel_id;
  const basicErrorHandlerArgs = {
    client,
    userId: command.user_id,
    replyChannelId: command.channel_id,
  };

  const { tools: preEnabledToolsList } = await getChannelSettings({
    teamId: context.teamId,
    enterpriseId: context.enterpriseId,
    channelId,
  });

  const getToolsListFromAPI = async () => {
    try {
      const toolkitClient = new ToolkitClient(OpenAPI);
      const tools = await toolkitClient.default.listToolsV1ToolsGet();

      return tools.filter((t) => t.is_available).map((tool) => tool.name);
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

  const apiToolsList = await getToolsListFromAPI();

  if (!apiToolsList) {
    await respond({
      response_type: 'ephemeral',
      text: `No tools are available in your account.`,
    });
    return;
  }

  const preEnabledToolsSet = new Set(preEnabledToolsList.map((t) => t.name));
  const formattedPreEnabledToolsList = apiToolsList.reduce<MrkdwnOption[]>((acc, tool) => {
    if (tool && preEnabledToolsSet.has(tool)) {
      acc.push({
        text: { type: 'mrkdwn', text: tool },
        value: tool,
      });
    }
    return acc;
  }, []);

  // Remove pre-enabled tools from the list of available tools so we can
  // Display those in a diff checkbox list
  const formattedAndSanitizedApiToolsList = apiToolsList.reduce<MrkdwnOption[]>((acc, tool) => {
    if (tool && !preEnabledToolsSet.has(tool)) {
      acc.push({
        text: { type: 'mrkdwn', text: tool },
        value: tool,
      });
    }
    return acc;
  }, []);

  // Slack only allows 1 - 10 options per checkbox block, so we need to group the tools
  let groupedTools = [];
  for (let i = 0; i < formattedAndSanitizedApiToolsList.length; i += 10) {
    const miniGroup = formattedAndSanitizedApiToolsList.slice(i, i + 10);
    groupedTools.push(miniGroup);
  }

  const formatterGroupedTools = groupedTools.map((group, index) => {
    return {
      block_id: `tools_list_block_${index}`,
      type: 'input',
      optional: true,
      element: {
        type: 'checkboxes',
        options: group,
        action_id: 'checkbox_action',
      },
      label: {
        type: 'plain_text',
        text:
          groupedTools.length > 1
            ? `Available Tools  ${index + 1}/${groupedTools.length}`
            : 'Available Tools',
        emoji: true,
      },
    };
  });

  const blocks = [
    formattedPreEnabledToolsList.length > 0 && {
      block_id: 'enabled_tools_list_block',
      type: 'input',
      optional: true,
      element: {
        type: 'checkboxes',
        options: formattedPreEnabledToolsList,
        initial_options: formattedPreEnabledToolsList,
        action_id: 'checkbox_action',
      },
      label: {
        type: 'plain_text',
        text: 'Enabled Tools',
        emoji: true,
      },
    },
    ...formatterGroupedTools,
  ].filter((n) => n) as KnownBlock[];

  await client.views
    .open({
      trigger_id: body.trigger_id,
      view: {
        private_metadata: JSON.stringify({
          channelId,
          numOfGroups: groupedTools.length,
          hasPreEnabledTools: formattedPreEnabledToolsList.length > 0,
        }),
        callback_id: 'tools_view',
        title: {
          type: 'plain_text',
          text: 'Tools Setup 🖇️',
          emoji: true,
        },
        blocks,
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
      },
    })
    .catch(
      async (error) =>
        await handleError({
          ...basicErrorHandlerArgs,
          replyThreadTs: command.thread_ts,
          customErrorMsg: error,
        }),
    );
};
