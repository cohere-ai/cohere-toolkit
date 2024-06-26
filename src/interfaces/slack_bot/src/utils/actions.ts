import {
  AppMentionEvent,
  BotMessageEvent,
  Context,
  FileShareMessageEvent,
  GenericMessageEvent,
  MessageEvent,
} from '@slack/bolt';
import { ConversationsRepliesResponse } from '@slack/web-api';

import { Tool } from '../cohere-client';
import { ACCEPTABLE_RAG_CHAT_FILE_TYPES, ACCEPTABLE_SUMMARIZE_FILE_TYPES } from '../constants';
import { SlackFile } from './files';
import { getChannelSettings } from './getChannelSettings';

export type SlackMessages = ConversationsRepliesResponse['messages'];

export type ActionEventTypes = AppMentionEvent | FileShareMessageEvent | GenericMessageEvent;

export type Action =
  | { type: 'chat'; event: ActionEventTypes }
  | { type: 'chat-rag'; event: ActionEventTypes; tools: Tool[] }
  | {
      type: 'file-summarize';
      event: ActionEventTypes;
      file: SlackFile;
    }
  | {
      type: 'file-rag';
      event: ActionEventTypes;
      file: SlackFile;
    }
  | {
      type: 'file-invalid';
      event: ActionEventTypes;
      originalAction: 'file-summarize' | 'file-rag';
    }
  | { type: 'ignore'; event: unknown };

export type ValidAction = Exclude<Action, { type: 'ignore' }>;

/**
 * Custom Type guards for Slack Events
 */
export const isFileShareEvent = (
  event: MessageEvent | AppMentionEvent,
): event is FileShareMessageEvent => {
  return (
    !!(event as FileShareMessageEvent).files ||
    (event.type === 'message' && event.subtype === 'file_share')
  );
};

export const isAppMentionEvent = (
  event: MessageEvent | AppMentionEvent,
): event is AppMentionEvent => {
  return event.type === 'app_mention';
};

const isGenericMessageEvent = (
  event: MessageEvent | AppMentionEvent,
): event is GenericMessageEvent => {
  return event.type === 'message' && event.subtype === undefined;
};

const isBotMessageEvent = (event: MessageEvent | AppMentionEvent): event is BotMessageEvent => {
  return event.type === 'message' && event.subtype === 'bot_message';
};

const isUnknownBotMessageEvent = (
  event: MessageEvent | AppMentionEvent,
): event is BotMessageEvent => {
  const botId = (event as BotMessageEvent).bot_id;
  if (!botId) return false; // No bot id means it's not a bot message

  const validBotIds = process.env.ALLOWED_BOT_IDS?.split(',') ?? [];
  const isValidBotId = validBotIds.includes((event as BotMessageEvent).bot_id);
  if (isValidBotId) return false; // If the bot id is valid, it's not an unknown bot

  return isBotMessageEvent(event);
};

/**
 * Determine the appropriate action based on the incoming slack event
 * and handle checks to ensure incompatible events are ignored
 */
export const determineAction = async (
  context: Context,
  event: MessageEvent | AppMentionEvent,
  messages: SlackMessages = [],
): Promise<Action> => {
  // never respond to unknown bots
  if (isUnknownBotMessageEvent(event)) return { type: 'ignore', event };

  // only support app mentions, file shares, bot, and generic messages
  // bot messages are allowed because all bot messages that reach this point are approved
  if (
    !isAppMentionEvent(event) &&
    !isGenericMessageEvent(event) &&
    !isFileShareEvent(event) &&
    !isBotMessageEvent(event)
  ) {
    return { type: 'ignore', event };
  }

  // if the message is empty, ignore the event
  if (event.text === undefined || event.text === '') return { type: 'ignore', event };

  // check if the event has a file or if there is a file in the history
  const eventFile = (event as FileShareMessageEvent).files?.[0];
  const file = eventFile || messages.find((m) => !!m.files)?.files?.[0];

  if (file) {
    const isUploadEvent = eventFile === file;
    const shouldSummarize = event.text?.includes('summarize');
    const isValidSummarizeFile =
      file?.url_private && ACCEPTABLE_SUMMARIZE_FILE_TYPES.has(file.filetype ?? 'unknown');
    const isValidRagFile =
      file?.url_private && ACCEPTABLE_RAG_CHAT_FILE_TYPES.has(file.filetype ?? 'unknown');

    if (shouldSummarize) {
      if (isValidSummarizeFile) {
        return { type: 'file-summarize', event, file };
      }
      // If the file is not a valid for summarization, default to chat, returning an error if the file was just uploaded
      return isUploadEvent
        ? { type: 'file-invalid', event, originalAction: 'file-summarize' }
        : { type: 'chat', event };
    }

    if (isValidRagFile) {
      return { type: 'file-rag', event, file };
    }

    // If the file is not a valid for rag chat, default to chat, returning an error if the file was just uploaded
    return isUploadEvent
      ? { type: 'file-invalid', event, originalAction: 'file-rag' }
      : { type: 'chat', event };
  }

  // Check if tools are enabled
  const { tools } = await getChannelSettings({
    teamId: context.teamId,
    enterpriseId: context.enterpriseId,
    channelId: event.channel,
  });

  if (tools.length > 0) {
    return {
      type: 'chat-rag',
      event,
      tools,
    };
  }
  // default to chat
  return { type: 'chat', event };
};
