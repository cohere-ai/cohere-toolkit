import {
  NonStreamedChatResponse,
  StreamCitationGeneration,
  StreamEnd,
  StreamEvent,
  StreamSearchQueriesGeneration,
  StreamSearchResults,
  StreamStart,
  StreamTextGeneration,
  StreamToolCallsChunk,
  StreamToolCallsGeneration,
  StreamToolInput,
  StreamToolResult,
} from '@/cohere-client';

type ChatResponseEventStreamStart = {
  event: StreamEvent.STREAM_START;
  data: StreamStart;
};

type ChatResponseEventTextGeneration = {
  event: StreamEvent.TEXT_GENERATION;
  data: StreamTextGeneration;
};

type ChatResponseEventSearchResults = {
  event: StreamEvent.SEARCH_RESULTS;
  data: StreamSearchResults;
};

type ChatResponseEventSearchQueriesGeneration = {
  event: StreamEvent.SEARCH_QUERIES_GENERATION;
  data: StreamSearchQueriesGeneration;
};

type ChatResponseEventToolCallsChunk = {
  event: StreamEvent.TOOL_CALLS_CHUNK;
  data: StreamToolCallsChunk;
};

type ChatResponseEventToolCallsGeneration = {
  event: StreamEvent.TOOL_CALLS_GENERATION;
  data: StreamToolCallsGeneration;
};

type ChatResponseEventCitationGeneration = {
  event: StreamEvent.CITATION_GENERATION;
  data: StreamCitationGeneration;
};

type ChatResponseEventToolInput = {
  event: StreamEvent.TOOL_INPUT;
  data: StreamToolInput;
};

type ChatResponseEventToolResult = {
  event: StreamEvent.TOOL_RESULT;
  data: StreamToolResult;
};

type ChatResponseEventStreamEnd = {
  event: StreamEvent.STREAM_END;
  data: StreamEnd;
};

type ChatResponseEventNonStreamedChatResponse = {
  event: StreamEvent.NON_STREAMED_CHAT_RESPONSE;
  data: NonStreamedChatResponse;
};

export type ChatResponseEvent =
  | ChatResponseEventStreamStart
  | ChatResponseEventTextGeneration
  | ChatResponseEventSearchResults
  | ChatResponseEventSearchQueriesGeneration
  | ChatResponseEventToolCallsChunk
  | ChatResponseEventCitationGeneration
  | ChatResponseEventToolInput
  | ChatResponseEventToolResult
  | ChatResponseEventToolCallsGeneration
  | ChatResponseEventStreamEnd
  | ChatResponseEventNonStreamedChatResponse;
