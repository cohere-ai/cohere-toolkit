/* generated using openapi-typescript-codegen -- do no edit */

/* istanbul ignore file */

/* tslint:disable */

/* eslint-disable */
import type { NonStreamedChatResponse } from './NonStreamedChatResponse';
import type { StreamCitationGeneration } from './StreamCitationGeneration';
import type { StreamEnd } from './StreamEnd';
import type { StreamEvent } from './StreamEvent';
import type { StreamQueryGeneration } from './StreamQueryGeneration';
import type { StreamSearchQueriesGeneration } from './StreamSearchQueriesGeneration';
import type { StreamSearchResults } from './StreamSearchResults';
import type { StreamStart } from './StreamStart';
import type { StreamTextGeneration } from './StreamTextGeneration';
import type { StreamToolInput } from './StreamToolInput';
import type { StreamToolResult } from './StreamToolResult';

export type ChatResponseEvent = {
  event: StreamEvent;
  data:
    | StreamStart
    | StreamTextGeneration
    | StreamCitationGeneration
    | StreamQueryGeneration
    | StreamSearchResults
    | StreamEnd
    | StreamToolInput
    | StreamToolResult
    | StreamSearchQueriesGeneration
    | NonStreamedChatResponse;
};
