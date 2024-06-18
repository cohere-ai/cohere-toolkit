/* generated using openapi-typescript-codegen -- do no edit */

/* istanbul ignore file */

/* tslint:disable */

/* eslint-disable */
import type { ToolCall } from './ToolCall';

/**
 * Stream tool calls generation event.
 */
export type StreamToolCallsGeneration = {
  tool_calls?: Array<ToolCall> | null;
  text: string | null;
};
