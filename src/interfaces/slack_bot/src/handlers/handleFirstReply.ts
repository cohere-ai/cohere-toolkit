import { Context, SayFn } from '@slack/bolt';
import { WebClient } from '@slack/web-api';

import { ALERTS, ERRORS, MAX_PROMPT_LENGTH, PENDING_MESSAGES } from '../constants';
import { ValidAction } from '../utils/actions';
import { getChannelSettings } from '../utils/getChannelSettings';
import { getConversationId } from '../utils/getConversationId';
import { getContentBlocks, getEphemeralBlocks, getFeedbackBlocks } from '../utils/getMessageBlocks';
import { getReply } from '../utils/getReply';
import { handleError, handleRagChatWithFile, handleSummarizeFile } from './';

type HandleFirstReplyArgs = {
  client: WebClient;
  action: ValidAction;
  context: Context;
  say: SayFn;
};

/**
 * This function deals with the first response which can be in a thread or in a DM
 */
export const handleFirstReply = async ({ context, action, client, say }: HandleFirstReplyArgs) => {
  const event = action.event;
  // If the message is not sent by a user, return
  if (!event.user) return;

  const userId = event.user;
  const channelId = event.channel;
  const eventTs = event.ts;
  const teamId = context.teamId;
  const enterpriseId = context.enterpriseId;
  const messageTs = event.ts;
  const basicErrorHandlerArgs = {
    client,
    userId,
    replyChannelId: channelId,
    replyThreadTs: eventTs,
    messageTs,
  };

  const { conversationId } = getConversationId({ threadTs: eventTs, channelId });

  const { deployment, model, temperature, preambleOverride } = await getChannelSettings({
    teamId,
    enterpriseId,
    channelId,
  });

  const msg = await say({
    text: PENDING_MESSAGES[action.type],
    thread_ts: eventTs,
  });

  if (!msg.ok || !msg.ts) {
    await handleError({
      customErrorMsg: ERRORS.GENERAL,
      ...basicErrorHandlerArgs,
    });
    return;
  }

  if (event.text && event.text.length > MAX_PROMPT_LENGTH) {
    await client.chat.postEphemeral({
      text: ALERTS.PROMPT_TOO_LONG,
      channel: channelId,
      user: userId,
      thread_ts: eventTs,
      blocks: getEphemeralBlocks({ text: ALERTS.PROMPT_TOO_LONG }),
    });
  }

  let responseID, currentBotReply, errorMessage;

  switch (action.type) {
    case 'file-summarize':
      ({ responseID, currentBotReply, errorMessage } = await handleSummarizeFile({
        file: action.file,
        teamId,
        enterpriseId,
        deployment,
        model,
      }));
      break;
    case 'file-rag':
      ({ responseID, currentBotReply, errorMessage } = await handleRagChatWithFile({
        client,
        text: event.text || '',
        file: action.file,
        deployment,
        model,
        teamId,
        botUserId: context.botUserId,
        enterpriseId,
        conversationId,
        isFirstMessage: true,
      }));
      break;
    case 'chat-rag':
      ({ responseID, currentBotReply, errorMessage } = await getReply({
        event: action.event,
        tools: action.tools,
        client,
        deployment,
        model,
        conversationId,
        temperature,
        preambleOverride,
        botUserId: context.botUserId,
        isFirstMessage: true,
      }));
      break;
    case 'file-invalid':
      await handleError({
        customErrorMsg:
          action.originalAction === 'file-rag'
            ? ERRORS.INVALID_RAG_CHAT_FILE_TYPE
            : ERRORS.INVALID_SUMMARIZE_FILE_TYPE,
        ...basicErrorHandlerArgs,
      });
    // We intentionally do not break here so we can fall through to normal chat
    case 'chat':
      ({ responseID, currentBotReply, errorMessage } = await getReply({
        event: action.event,
        client,
        deployment,
        model,
        conversationId,
        temperature,
        preambleOverride,
        botUserId: context.botUserId,
        isFirstMessage: true,
      }));
      break;
    default:
      return;
  }

  if (errorMessage || !currentBotReply || !responseID) {
    await handleError({
      customErrorMsg: errorMessage ? `${ERRORS.PREFIX} ${errorMessage}` : ERRORS.GENERAL,
      ...basicErrorHandlerArgs,
    });
    await client.chat.delete({
      channel: channelId,
      ts: msg.ts,
    });
    return;
  }

  // Allows for easy backtracking from response to backend call to address potential issues
  const { permalink } = await client.chat.getPermalink({
    channel: channelId,
    message_ts: msg.ts,
  });
  console.log(`New Generation: ${permalink} - ${responseID}`);

  // We chunk by 2990 to allow space for the message number and total message count
  // The extra 10 characters allows for up to 999 messages: "[999/999] "
  // The last character is the word boundary if it is included in the chunk
  let rawMsgChunks = currentBotReply.match(
    /[\w\W]{1,2989}(?:[\p{Punctuation}|\p{White_Space}]|$)+?/gmu,
  );

  // If the message can't be chunked properly, we have to chunk without respecting word boundaries
  if (!rawMsgChunks || rawMsgChunks.join('').length !== currentBotReply.length) {
    rawMsgChunks = currentBotReply.match(/[\w\W]{1,2989}/gm);
  }

  const msgChunks = rawMsgChunks?.map((s) => s.trim()) || [];
  const totalChunkCount = msgChunks.length;
  const lastChunk = msgChunks.pop() || '';

  for (const [idx, chunk] of msgChunks.entries()) {
    const chunkWithNumber = `[${idx + 1}/${totalChunkCount}] ${chunk}`;
    const contentBlocks = getContentBlocks(chunkWithNumber);

    await say({
      text: chunk,
      thread_ts: eventTs,
      blocks: [...contentBlocks],
    });
  }

  const lastChunkWithNumber = `[${totalChunkCount}/${totalChunkCount}] ${lastChunk}`;
  const lastChunkContentBlock = getContentBlocks(
    totalChunkCount > 1 ? lastChunkWithNumber : lastChunk,
  );
  const feedbackBlocks = getFeedbackBlocks({
    responseID,
    threadTs: eventTs,
  });

  await client.chat.delete({
    channel: channelId,
    ts: msg.ts,
  });

  await say({
    text: lastChunk,
    thread_ts: eventTs,
    blocks: [...lastChunkContentBlock, ...feedbackBlocks],
  });
};
