/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChatMessage } from './ChatMessage';
import type { Citation } from './Citation';
import type { Document } from './Document';
import type { SearchQuery } from './SearchQuery';
import type { ToolCall } from './ToolCall';
export type NonStreamedChatResponse = {
    is_finished: boolean;
    response_id: (string | null);
    generation_id: (string | null);
    chat_history: (Array<ChatMessage> | null);
    finish_reason: string;
    text: string;
    citations?: (Array<Citation> | null);
    documents?: (Array<Document> | null);
    search_results?: null;
    search_queries?: (Array<SearchQuery> | null);
    conversation_id: (string | null);
    tool_calls?: (Array<ToolCall> | null);
};

