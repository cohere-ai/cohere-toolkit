/* generated using openapi-typescript-codegen -- do no edit */

/* istanbul ignore file */

/* tslint:disable */

/* eslint-disable */
import type { CreateAgentToolMetadata } from './CreateAgentToolMetadata';

export type CreateAgent = {
  name: string;
  version?: number | null;
  description?: string | null;
  preamble?: string | null;
  temperature?: number | null;
  model: string;
  deployment: string;
  tools?: Array<string> | null;
  tools_metadata?: Array<CreateAgentToolMetadata> | null;
};
