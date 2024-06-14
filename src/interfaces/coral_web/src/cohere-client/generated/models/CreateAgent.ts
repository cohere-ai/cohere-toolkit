/* generated using openapi-typescript-codegen -- do no edit */

/* istanbul ignore file */

/* tslint:disable */

/* eslint-disable */
import type { AgentDeployment } from './AgentDeployment';
import type { AgentModel } from './AgentModel';
import type { ToolName } from './ToolName';

export type CreateAgent = {
  name: string;
  version?: number | null;
  description?: string | null;
  preamble?: string | null;
  temperature?: number | null;
  model: AgentModel;
  deployment?: AgentDeployment | null;
  tools?: Array<ToolName> | null;
};
