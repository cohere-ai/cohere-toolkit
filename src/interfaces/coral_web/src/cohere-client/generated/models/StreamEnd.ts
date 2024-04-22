/* generated using openapi-typescript-codegen -- do no edit */

/* istanbul ignore file */

/* tslint:disable */

/* eslint-disable */
import type { Citation } from './Citation';
import type { Document } from './Document';
import type { SearchQuery } from './SearchQuery';

export type StreamEnd = {
  response_id: string;
  generation_id: string;
  conversation_id: string | null;
  text: string;
  citations?: Array<Citation>;
  documents?: Array<Document>;
  search_results?: Array<Record<string, any>>;
  search_queries?: Array<SearchQuery>;
  finish_reason: string;
};
