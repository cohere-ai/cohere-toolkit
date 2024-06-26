import {
  AckFn,
  AllMiddlewareArgs,
  AppMentionEvent,
  Context,
  DialogValidation,
  MessageEvent,
  RespondFn,
  SayArguments,
  SectionBlock,
  SlackAction,
} from '@slack/bolt';

import { ERRORS, STOP_REPLYING_MESSAGE } from '../constants';

type Message = MessageEvent | AppMentionEvent;

type HandleStopConversationArgs = Pick<AllMiddlewareArgs, 'client'> & {
  ack: AckFn<void> | AckFn<string | SayArguments> | AckFn<DialogValidation>;
  body: SlackAction;
  respond: RespondFn;
};

type RemoveFeedbackButtonArgs = Pick<AllMiddlewareArgs, 'client'> & {
  channel: string;
  text: string;
  ts: string;
};

type RemovePrevBotMsgFeedbackButtonsArgs = Pick<AllMiddlewareArgs, 'client'> & {
  channel: string;
  context: Context;
  messageHistory: Array<Message>;
};

/**
 * Replaces message content with just the text, thereby removing any buttons or other interactive additions
 * This is used to remove the feedback buttons after the user has clicked one
 * Can also be used to update text after a user has submitted a rewritten response
 */
const removeFeedbackButtons = async ({ client, channel, text, ts }: RemoveFeedbackButtonArgs) => {
  await client.chat.update({
    channel,
    ts,
    text,
    blocks: [
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: text,
        },
      },
    ],
  });
};

/**
 * Removes the feedback buttons from prior bot responses
 * This is to ensure that the conversation history won't be significantly altered
 * in the middle of a conversation
 */
export const removePrevBotMsgFeedbackButtons = async ({
  client,
  context,
  channel,
  messageHistory,
}: RemovePrevBotMsgFeedbackButtonsArgs) => {
  const filteredMessageHistory = messageHistory.filter(
    /**
     * Check 1: We only care about messages, not events; Gets rid of TS weirdness
     * Check 3: Feedback buttons are only generated from block actions
     *          If we remove all of the block actions, it shows as edited
     */
    (msg) =>
      msg.subtype === undefined &&
      msg.user === context.botUserId &&
      msg.blocks?.some((block) => block.type === 'actions'),
  );

  for (let message of filteredMessageHistory) {
    // We only care about messages, not events; Gets rid of TS weirdness
    if (message.subtype !== undefined) continue;

    let text = message.text ?? '';
    let sectionBlocks = message.blocks?.filter((block) => block.type === 'section');
    if (sectionBlocks) {
      // TS doesn't understand that we've already checked for this in the filter
      let typedSectionBlock = sectionBlocks[0] as SectionBlock;
      text = typedSectionBlock.text?.text ?? text;
    }

    await removeFeedbackButtons({
      client,
      channel,
      text,
      ts: message.ts,
    });
  }
};

export const handleStopConversation = async ({
  client,
  ack,
  body,
  respond,
}: HandleStopConversationArgs) => {
  await ack();

  // Stop buttons are only generated from block actions
  if (body.type !== 'block_actions') {
    await respond({
      response_type: 'ephemeral',
      text: ERRORS.GENERAL,
    });
    console.error("handleStopConversation: body.type !== 'block_actions'");
    return;
  }

  // Stop button should be a... button
  if (body.actions[0].type !== 'button') {
    await respond({
      response_type: 'ephemeral',
      text: ERRORS.GENERAL,
    });
    console.error("handleStopConversation: body.actions[0].type !== 'button'");
    return;
  }

  // Feedback buttons should only exist on messages
  if (!body.message) {
    await respond({
      response_type: 'ephemeral',
      text: ERRORS.GENERAL,
    });
    console.error('handleUserFeedback: !body.message');
    return;
  }

  // Messages have to exist in channels
  if (!body.channel) {
    await respond({
      response_type: 'ephemeral',
      text: ERRORS.GENERAL,
    });
    console.error('handleUserFeedback: !body.channel');
    return;
  }

  await client.chat.postMessage({
    channel: body.channel.id,
    thread_ts: body.message.ts,
    text: STOP_REPLYING_MESSAGE,
  });

  await removeFeedbackButtons({
    client,
    channel: body.channel.id,
    text: body.message.text || '',
    ts: body.message.ts,
  });
};
