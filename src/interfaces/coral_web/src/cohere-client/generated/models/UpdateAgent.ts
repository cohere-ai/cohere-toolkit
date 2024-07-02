/* generated using openapi-typescript-codegen -- do no edit */

/* istanbul ignore file */

/* tslint:disable */

/* eslint-disable */
import type { AgentToolMetadata } from './AgentToolMetadata';

export type UpdateAgent = {
  name?: string | null;
  version?: number | null;
  description?: string | null;
  preamble?: string | null;
  temperature?: number | null;
  model?: string | null;
  deployment?: string | null;
  tools?: Array<string> | null;
  tools_metadata?: Array<AgentToolMetadata> | null;
};
