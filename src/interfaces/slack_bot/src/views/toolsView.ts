import { Middleware, SlackViewMiddlewareArgs } from '@slack/bolt';

import { prisma } from '..';

// Extract the selected tools from the view and save them to the database
export const toolsView: Middleware<SlackViewMiddlewareArgs> = async ({ ack, view, context }) => {
  const { channelId, hasPreEnabledTools, numOfGroups } = JSON.parse(view['private_metadata']);

  let selectedTools = [];
  for (let i = 0; i < numOfGroups; i++) {
    const selectedTool =
      view['state']['values'][`tools_list_block_${i}`]['checkbox_action']['selected_options'];
    if (selectedTool) {
      selectedTools.push(...selectedTool);
    }
  }

  if (hasPreEnabledTools) {
    const selectedPreEnabledTools =
      view['state']['values']['enabled_tools_list_block']['checkbox_action']['selected_options'];
    if (selectedPreEnabledTools) {
      selectedTools.push(...selectedPreEnabledTools);
    }
  }

  if (!selectedTools) {
    return;
  }
  const selectedToolNamesArray = selectedTools.map((tool) => tool.value);
  const toolsMessage =
    selectedToolNamesArray.length > 0
      ? `Tools enabled for this channel:\n • ${selectedToolNamesArray.join('\n • ')}`
      : 'All tools have been disabled of this channel.';
  await ack({
    response_action: 'update',
    view: {
      callback_id: 'tools_view_success',
      title: {
        type: 'plain_text',
        text: 'Tools Setup 🖇️',
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
          block_id: 'description_block',
          text: {
            type: 'mrkdwn',
            text: toolsMessage,
          },
        },
      ],
    },
  });

  const workspaceSettings = await prisma.workspaceSettings.upsert({
    create: { teamId: context.teamId, enterpriseId: context.enterpriseId },
    update: {},
    where: { teamId: context.teamId, enterpriseId: context.enterpriseId },
  });

  await prisma.channelSettings.upsert({
    create: {
      channelId,
      workspaceId: workspaceSettings.id,
      tools: selectedToolNamesArray,
    },
    update: { tools: selectedToolNamesArray },
    where: {
      channelSettingsId: {
        channelId,
        workspaceId: workspaceSettings.id,
      },
    },
  });
};
