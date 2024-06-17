/* generated using openapi-typescript-codegen -- do no edit */

/* istanbul ignore file */

/* tslint:disable */

/* eslint-disable */
import type { Citation } from './Citation';
import type { Document } from './Document';
import type { SearchQuery } from './SearchQuery';
import type { ToolCall } from './ToolCall';

export type StreamEnd = {
  response_id?: string | null;
  generation_id?: string | null;
  conversation_id?: string | null;
  text: string;
  citations?: Array<Citation>;
  documents?: Array<Document>;
  search_results?: Array<Record<string, any>>;
  search_queries?: Array<SearchQuery>;
  tool_calls?: Array<ToolCall>;
  finish_reason?: string | null;
};
