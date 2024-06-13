/* generated using openapi-typescript-codegen -- do no edit */

/* istanbul ignore file */

/* tslint:disable */

/* eslint-disable */
import type { AgentDeployment } from './AgentDeployment';
import type { AgentModel } from './AgentModel';
import type { ToolName } from './ToolName';

export type UpdateAgent = {
  name?: string | null;
  version?: number | null;
  description?: string | null;
  preamble?: string | null;
  temperature?: number | null;
  model?: AgentModel | null;
  deployment?: AgentDeployment | null;
  tools?: Array<ToolName> | null;
};
