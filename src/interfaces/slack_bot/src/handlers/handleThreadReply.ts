import {
  AllMiddlewareArgs,
  AppMentionEvent,
  Context,
  MessageEvent,
  RespondFn,
  SayFn,
} from '@slack/bolt';

import {
  ALERTS,
  ERRORS,
  MAX_PROMPT_LENGTH,
  PENDING_MESSAGES,
  STOP_REPLYING_MESSAGE,
} from '../constants';
import { SlackMessages, ValidAction } from '../utils/actions';
import { getChannelSettings } from '../utils/getChannelSettings';
import { getConversationId } from '../utils/getConversationId';
import { getContentBlocks, getEphemeralBlocks, getFeedbackBlocks } from '../utils/getMessageBlocks';
import { getReply } from '../utils/getReply';
import { getSanitizedConversationHistory } from '../utils/getSanitizedConversationHistory';
import {
  handleError,
  handleRagChatWithFile,
  handleSummarizeFile,
  removePrevBotMsgFeedbackButtons,
} from './';

type HandleThreadReplyArgs = Pick<AllMiddlewareArgs, 'client'> & {
  context: Context;
  action: ValidAction;
  messages: SlackMessages;
  say: SayFn | RespondFn;
};

/**
 * This function deals with all thread replies within channels and group messages
 * excluding the first reply (app mention)
 */
export const handleThreadReply = async ({
  context,
  action,
  client,
  messages,
  say,
}: HandleThreadReplyArgs) => {
  const event = action.event;
  // If the message is not sent by a user, return
  if (!event.user) return;
  // If the message is not in a thread, return
  if (!event.thread_ts) return;

  const threadTs = event.thread_ts;
  const threadChannelId = event.channel;
  const userId = event.user;
  const messageTs = event.ts;
  const basicErrorHandlerArgs = {
    client,
    userId,
    replyChannelId: threadChannelId,
    replyThreadTs: threadTs,
    messageTs,
  };
  const teamId = context.teamId;
  const enterpriseId = context.enterpriseId;

  const { deployment, model, temperature, preambleOverride } = await getChannelSettings({
    teamId,
    enterpriseId,
    channelId: threadChannelId,
  });

  const { conversationId } = getConversationId({
    threadTs,
    channelId: threadChannelId,
  });

  // If there's no message history, this event shouldn't have been triggered
  if (!messages) return;

  const { hasStopReplyingCommand, hasBotAckStopReplyingCommand } =
    await getSanitizedConversationHistory({
      context,
      client,
      // the "as" is needed to convert back to Bolt types
      messageHistory: messages as Array<MessageEvent | AppMentionEvent>,
    });
  if (hasBotAckStopReplyingCommand) return;
  if (hasStopReplyingCommand) {
    await say({
      text: STOP_REPLYING_MESSAGE,
      thread_ts: threadTs,
    });

    await removePrevBotMsgFeedbackButtons({
      client,
      context,
      channel: threadChannelId,
      messageHistory: messages as Array<MessageEvent>,
    });
    return;
  }

  const msg = await say({
    text: PENDING_MESSAGES[action.type],
    thread_ts: threadTs,
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
      channel: threadChannelId,
      user: userId,
      thread_ts: threadTs,
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
    // Intentionally fall through to normal chat
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

  if (!currentBotReply || !responseID || errorMessage) {
    await client.chat.delete({
      channel: threadChannelId,
      ts: msg.ts,
    });
    await handleError({
      customErrorMsg: errorMessage ? `${ERRORS.PREFIX} ${errorMessage}` : ERRORS.CHAT,
      ...basicErrorHandlerArgs,
    });

    return;
  }

  // Allows for easy backtracking from response to backend call to address potential issues
  const { permalink } = await client.chat.getPermalink({
    channel: msg.channel,
    message_ts: msg.ts,
  });
  console.log(`New Generation: ${permalink} - ${responseID}`);

  await removePrevBotMsgFeedbackButtons({
    client,
    context,
    channel: threadChannelId,
    messageHistory: messages as Array<MessageEvent>,
  });

  // We chunk by 2990 to allow space for the message number and total message count
  // The extra 10 characters allows for up to 999 messages: "[999/999] "
  // The extra character is the word boundary if it is included in the chunk
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
      thread_ts: threadTs,
      blocks: [...contentBlocks],
    });
  }

  const lastChunkWithNumber = `[${totalChunkCount}/${totalChunkCount}] ${lastChunk}`;
  const lastChunkContentBlock = getContentBlocks(
    totalChunkCount > 1 ? lastChunkWithNumber : lastChunk,
  );
  const feedbackBlocks = getFeedbackBlocks({
    responseID,
    threadTs: threadTs,
  });

  await client.chat.delete({
    channel: threadChannelId,
    ts: msg.ts,
  });

  await say({
    text: lastChunk,
    thread_ts: threadTs,
    blocks: [...lastChunkContentBlock, ...feedbackBlocks],
  });
};
