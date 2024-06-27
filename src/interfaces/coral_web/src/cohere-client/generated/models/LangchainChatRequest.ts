/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChatMessage } from './ChatMessage';
import type { Tool } from './Tool';
/**
 * Request shape for Langchain Streamed Chat.
 */
export type LangchainChatRequest = {
    message: string;
    chat_history?: (Array<ChatMessage> | null);
    conversation_id?: string;
    tools?: (Array<Tool> | null);
};

