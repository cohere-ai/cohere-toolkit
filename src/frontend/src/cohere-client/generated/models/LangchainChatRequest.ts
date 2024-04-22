/* generated using openapi-typescript-codegen -- do no edit */

/* istanbul ignore file */

/* tslint:disable */

/* eslint-disable */
import type { ChatMessage } from './ChatMessage';
import type { Tool } from './Tool';

/**
 * Request shape for Langchain Streamed Chat.
 * See: https://github.com/cohere-ai/cohere-python/blob/main/src/cohere/base_client.py#L1629
 */
export type LangchainChatRequest = {
  message: string;
  chat_history?: Array<ChatMessage> | null;
  conversation_id?: string;
  preamble?: string | null;
  tools?: Array<Tool>;
};
