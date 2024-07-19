import { Citation, File, StreamToolCallsGeneration, StreamToolInput } from '@/cohere-client';

export enum BotState {
  LOADING = 'loading',
  TYPING = 'typing',
  FULFILLED = 'fulfilled',
  ERROR = 'error',
  ABORTED = 'aborted',
}

export enum MessageType {
  BOT = 'bot',
  USER = 'user',
}

type BaseMessage = {
  type: MessageType;
  text: string;
  error?: string;
};

/**
 * This is a bot-only state for all past bot messages that have been returned from the server.
 */
export type FulfilledMessage = BaseMessage & {
  type: MessageType.BOT;
  state: BotState.FULFILLED;
  /**
   * Unique Id per generation for given responseId
   * A responseId can have multiple generations
   */
  generationId: string;
  /* This id links a particular message to a piece of feedback given by the user. */
  feedbackId?: string;
  goodResponse?: boolean;
  citations?: Citation[];
  isRAGOn?: boolean;
  originalText: string;
  toolEvents?: StreamToolCallsGeneration[];
};

/**
 * This is a bot-only state for when a message is aborted.
 */
export type AbortedMessage = BaseMessage & {
  type: MessageType.BOT;
  state: BotState.ABORTED;
  toolEvents?: StreamToolCallsGeneration[];
};

/**
 * This is a bot-only state for when we wait for the bot's first token to arrive.
 */
export type LoadingMessage = BaseMessage & {
  type: MessageType.BOT;
  state: BotState.LOADING;
  isRAGOn?: boolean;
};

/**
 * This is a bot-only state for when we are streaming in tokens.
 */
export type TypingMessage = BaseMessage & {
  type: MessageType.BOT;
  state: BotState.TYPING;
  generationId: string;
  originalText: string;
  citations?: Citation[];
  isRAGOn?: boolean;
  toolEvents?: StreamToolCallsGeneration[];
};

/**
 * This is a bot-only state for when there is an error from the server.
 */
export type ErrorMessage = BaseMessage & {
  type: MessageType.BOT;
  state: BotState.ERROR;
  toolEvents?: StreamToolInput[];
};

/**
 * Message sent from the user.
 */
export type UserMessage = BaseMessage & {
  type: MessageType.USER;
  files?: File[];
};

export type ChatMessage = UserMessage | BotMessage;

export type BotMessage =
  | LoadingMessage
  | TypingMessage
  | FulfilledMessage
  | ErrorMessage
  | AbortedMessage;

export type StreamingMessage = FulfilledMessage | TypingMessage | LoadingMessage;

export const isUserMessage = (message: ChatMessage): message is UserMessage => {
  return message.type === MessageType.USER;
};

export const isFulfilledMessage = (message: ChatMessage): message is FulfilledMessage => {
  return message.type === MessageType.BOT && message.state === BotState.FULFILLED;
};

export const isErroredMessage = (message: ChatMessage): message is ErrorMessage => {
  return message.type == MessageType.BOT && message.state === BotState.ERROR;
};

export const isTypingMessage = (message: ChatMessage): message is TypingMessage => {
  return message.type === MessageType.BOT && message.state === BotState.TYPING;
};

export const isLoadingMessage = (message: ChatMessage): message is TypingMessage => {
  return message.type === MessageType.BOT && message.state === BotState.LOADING;
};

export const isAbortedMessage = (message: ChatMessage): message is AbortedMessage => {
  return message.type === MessageType.BOT && message.state === BotState.ABORTED;
};

export const isFulfilledOrTypingMessage = (
  message: ChatMessage
): message is FulfilledMessage | TypingMessage => {
  return isFulfilledMessage(message) || isTypingMessage(message);
};

export const isFulfilledOrTypingMessageWithCitations = (
  m: ChatMessage
): m is FulfilledMessage | (TypingMessage & Required<Pick<FulfilledMessage, 'citations'>>) =>
  m && isFulfilledOrTypingMessage(m) && !!m.citations && m.citations.length > 0;

export const createErrorMessage = (message: Omit<ErrorMessage, 'type' | 'state'>): ErrorMessage => {
  return {
    ...message,
    type: MessageType.BOT,
    state: BotState.ERROR,
  };
};

export const createAbortedMessage = (
  message: Omit<AbortedMessage, 'type' | 'state'>
): AbortedMessage => {
  return {
    ...message,
    type: MessageType.BOT,
    state: BotState.ABORTED,
  };
};

export const createLoadingMessage = (
  message: Omit<LoadingMessage, 'type' | 'state'>
): LoadingMessage => {
  return {
    ...message,
    type: MessageType.BOT,
    state: BotState.LOADING,
  };
};
