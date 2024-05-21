/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChatMessage } from './ChatMessage';
import type { CohereChatPromptTruncation } from './CohereChatPromptTruncation';
import type { Tool } from './Tool';
/**
 * Request shape for Cohere Python SDK Streamed Chat.
 * See: https://github.com/cohere-ai/cohere-python/blob/main/src/cohere/base_client.py#L1629
 */
export type CohereChatRequest = {
    message: string;
    chat_history?: (Array<ChatMessage> | null);
    conversation_id?: string;
    tools?: (Array<Tool> | null);
    documents?: Array<Record<string, any>>;
    model?: (string | null);
    temperature?: (number | null);
    'k'?: (number | null);
    'p'?: (number | null);
    preamble?: (string | null);
    file_ids?: (Array<string> | null);
    search_queries_only?: (boolean | null);
    max_tokens?: (number | null);
    seed?: (number | null);
    stop_sequences?: (Array<string> | null);
    presence_penalty?: (number | null);
    frequency_penalty?: (number | null);
    prompt_truncation?: CohereChatPromptTruncation;
};

